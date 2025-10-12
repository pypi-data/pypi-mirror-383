import base64
import os
import subprocess  # noqa
from datetime import timedelta
from tempfile import TemporaryDirectory
from typing import Callable, Optional
from urllib.parse import urljoin

from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.http import HttpRequest, HttpResponseRedirect
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import get_language
from django.utils.translation import gettext as _

from celery.result import AsyncResult
from celery_progress.backend import ProgressRecorder
from selenium import webdriver
from selenium.webdriver.common.print_page_options import PrintOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

from aleksis.core.celery import app
from aleksis.core.models import PDFFile, TaskUserAssignment
from aleksis.core.util.celery_progress import recorded_task
from aleksis.core.util.core_helpers import has_person, process_custom_context_processors


def _generate_pdf_with_webdriver(
    temp_dir: str, pdf_path: str, html_url: str, lang: str, page_count: Optional[int | str] = None
):
    """Generate a PDF file from a HTML file."""
    driver_options = webdriver.FirefoxOptions()
    driver_options.add_argument("--headless")
    driver_options.add_argument(f"--lang={lang}")

    if settings.SELENIUM_URL is None:
        driver_manager = GeckoDriverManager()
        service = FirefoxService(
            driver_manager.install(), service_args=["--profile-root", temp_dir]
        )

        driver = webdriver.Firefox(service=service, options=driver_options)
    else:
        driver = webdriver.Remote(command_executor=settings.SELENIUM_URL, options=driver_options)

    driver.get(html_url)
    print_options = PrintOptions()
    print_options.shrink_to_fit = False
    print_options.background = True
    print_options.margin_top = 0
    print_options.margin_left = 0
    print_options.margin_right = 0
    print_options.margin_bottom = 0
    if page_count is not None:
        print_options.page_ranges = [
            f"1-{page_count}" if isinstance(page_count, int) else page_count
        ]
    pdf = driver.print_page(print_options)
    driver.quit()
    with open(pdf_path, "wb") as f:
        f.write(base64.b64decode(pdf))


@recorded_task
def generate_pdf(
    file_pk: int,
    html_url: str,
    recorder: ProgressRecorder,
    lang: Optional[str] = None,
    page_count: Optional[int] = None,
):
    """Generate a PDF file by rendering the HTML code using a headless Firefox."""
    file_object = get_object_or_404(PDFFile, pk=file_pk)

    recorder.set_progress(0, 1)

    # Open a temporary directory
    with TemporaryDirectory() as temp_dir:
        pdf_path = os.path.join(temp_dir, "print.pdf")
        lang = lang or get_language()

        _generate_pdf_with_webdriver(temp_dir, pdf_path, html_url, lang=lang, page_count=page_count)

        # Upload PDF file to media storage
        with open(pdf_path, "rb") as f:
            file_object.file.save("print.pdf", File(f))
            file_object.save()

    recorder.set_progress(1, 1)


def process_context_for_pdf(context: Optional[dict] = None, request: Optional[HttpRequest] = None):
    context = context or {}
    if not request:
        processed_context = process_custom_context_processors(
            settings.NON_REQUEST_CONTEXT_PROCESSORS
        )
        processed_context.update(context)
    else:
        processed_context = context
    return processed_context


def generate_pdf_from_html(
    html: str,
    request: Optional[HttpRequest] = None,
    file_object: Optional[PDFFile] = None,
    task_user_assignment: Optional[TaskUserAssignment] = None,
    page_count: Optional[int] = None,
) -> tuple[PDFFile, AsyncResult | TaskUserAssignment]:
    """Start a PDF generation task and return the matching file object and Celery result."""
    html_file = ContentFile(html.encode(), name="source.html")

    # In some cases, the file object is already created (to get a redirect URL for the PDF)
    if not file_object:
        file_object = PDFFile.objects.create()
    if request and has_person(request):
        file_object.person = request.user.person
    file_object.html_file = html_file
    file_object.save()

    # As this method may be run in background and there is no request available,
    # we have to use a predefined URL from settings then
    if request:
        html_url = request.build_absolute_uri(file_object.html_file.url)
    else:
        html_url = urljoin(settings.BASE_URL, file_object.html_file.url)

    if task_user_assignment:
        result = generate_pdf.delay_with_progress(
            task_user_assignment,
            file_object.pk,
            html_url,
            lang=get_language(),
            page_count=page_count,
        )
    else:
        result = generate_pdf.delay(
            file_object.pk, html_url, lang=get_language(), page_count=page_count
        )
    return file_object, result


def generate_pdf_from_template(
    template_name: str,
    context: Optional[dict] = None,
    request: Optional[HttpRequest] = None,
    render_method: Optional[Callable] = None,
    file_object: Optional[PDFFile] = None,
    task_user_assignment: Optional[TaskUserAssignment] = None,
    page_count: Optional[int | str] = None,
) -> tuple[PDFFile, AsyncResult | TaskUserAssignment]:
    """Start a PDF generation task and return the matching file object and Celery result."""
    processed_context = process_context_for_pdf(context, request)

    if render_method:
        html_template = render_method(processed_context, request)
    else:
        html_template = render_to_string(template_name, processed_context, request)

    return generate_pdf_from_html(
        html_template,
        request,
        file_object=file_object,
        task_user_assignment=task_user_assignment,
        page_count=page_count,
    )


def render_pdf(
    request: HttpRequest,
    template_name: str,
    context: dict = None,
    page_count: Optional[int | str] = None,
) -> HttpResponse:
    """Start PDF generation and show progress page.

    The progress page will redirect to the PDF after completion.
    """
    if not context:
        context = {}

    user_assignment = TaskUserAssignment(
        user=request.user,
        title=_("Progress: Generate PDF file"),
        progress_title=_("Generating PDF file …"),
        success_message=_("The PDF file has been generated successfully."),
        error_message=_("There was a problem while generating the PDF file."),
        back_url=context.get("back_url", reverse("index")),
        additional_button_title=_("Download PDF"),
        additional_button_icon="mdi-file-pdf-box",
    )

    file_object, result = generate_pdf_from_template(
        template_name, context, request, task_user_assignment=user_assignment, page_count=page_count
    )

    result.redirect_on_success_url = f"/pdfs/{file_object.pk}"
    result.button_url = result.redirect_on_success_url
    result.save()

    return HttpResponseRedirect(result.get_absolute_url())


def clean_up_expired_pdf_files() -> None:
    """Clean up expired PDF files."""
    PDFFile.objects.filter(expires_at__lt=timezone.now()).delete()


@app.task(run_every=timedelta(days=1))
def clean_up_expired_pdf_files_task() -> None:
    """Clean up expired PDF files."""
    return clean_up_expired_pdf_files()
