$(".copy-button").click((e) => {
  const target = $(e.currentTarget);
  const input = $("#" + target.data("target"));
  const copy_icon = target.children(".copy-icon-copy").first();
  const check_icon = target.children(".copy-icon-success").first();

  console.log("Copying to clipboard");
  navigator.clipboard.writeText(input.val()).then((r) => {
    check_icon.show();
    copy_icon.hide();
    setTimeout(() => {
      check_icon.hide();
      copy_icon.show();
    }, 1000);
  });
});
