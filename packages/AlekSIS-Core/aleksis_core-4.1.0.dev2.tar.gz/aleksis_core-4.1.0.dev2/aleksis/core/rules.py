import rules
from rules import is_superuser

from .models import Announcement, AvailabilityEvent, GroupType, Holiday, Organisation, Role, Room
from .util.predicates import (
    has_any_group,
    has_any_object,
    has_any_person,
    has_global_perm,
    has_object_perm,
    has_person,
    has_person_email,
    has_person_user,
    is_anonymous,
    is_current_person,
    is_dashboard_widget_instance_owner,
    is_dummy,
    is_group_owner,
    is_group_owner_allowed_information,
    is_group_owner_of_person_with_group_type,
    is_group_owner_with_group_type,
    is_notification_recipient,
    is_own_availability_event,
    is_own_celery_task,
    is_personal_event_owner,
    is_personal_todo_owner,
    is_site_preference_set,
)

rules.add_perm("core", rules.always_allow)

# Login
login_predicate = is_anonymous
rules.add_perm("core.login_rule", login_predicate)

# Logout
logout_predicate = ~is_anonymous
rules.add_perm("core.logout_rule", logout_predicate)

# Account
view_account_predicate = has_person
rules.add_perm("core.view_account_rule", view_account_predicate)

# 2FA
manage_2fa_predicate = has_person
rules.add_perm("core.manage_2fa_rule", manage_2fa_predicate)

# Social Connections
manage_social_connections_predicate = has_person
rules.add_perm("core.manage_social_connections_rule", manage_social_connections_predicate)

# Authorized tokens
manage_authorized_tokens_predicate = has_person
rules.add_perm("core.manage_authorized_tokens_rule", manage_authorized_tokens_predicate)

# View dashboard
view_dashboard_predicate = is_site_preference_set("general", "anonymous_dashboard") | has_person
rules.add_perm("core.view_dashboard_rule", view_dashboard_predicate)

# View notifications
rules.add_perm("core.view_notifications_rule", has_person)

# Use search
search_predicate = has_person & has_global_perm("core.search")
rules.add_perm("core.search_rule", search_predicate)

# View persons
view_persons_predicate = has_person & (has_global_perm("core.view_person") | has_any_person)
rules.add_perm("core.view_persons_rule", view_persons_predicate)

# View person
view_person_predicate = has_person & (
    is_current_person
    | has_global_perm("core.view_person")
    | has_object_perm("core.view_person")
    | is_group_owner_of_person_with_group_type
)
rules.add_perm("core.view_person_rule", view_person_predicate)

# View person addresses
view_addresses_predicate = has_person & (
    is_current_person
    | has_global_perm("core.view_addresses")
    | has_object_perm("core.view_addresses")
    | (is_group_owner_of_person_with_group_type & is_group_owner_allowed_information("address"))
)
rules.add_perm("core.view_addresses_rule", view_addresses_predicate)

# View person contact details
view_contact_details_predicate = has_person & (
    is_current_person
    | has_global_perm("core.view_contact_details")
    | has_object_perm("core.view_contact_details")
    | (
        is_group_owner_of_person_with_group_type
        & is_group_owner_allowed_information("contact_details")
    )
)
rules.add_perm("core.view_contact_details_rule", view_contact_details_predicate)

# View person photo
view_photo_predicate = has_person & (
    is_current_person
    | has_global_perm("core.view_photo")
    | has_object_perm("core.view_photo")
    | (is_group_owner_of_person_with_group_type & is_group_owner_allowed_information("photo"))
)
rules.add_perm("core.view_photo_rule", view_photo_predicate)

# View person avatar image
view_avatar_predicate = has_person & (
    is_current_person
    | has_global_perm("core.view_avatar")
    | has_object_perm("core.view_avatar")
    | (is_group_owner_of_person_with_group_type & is_group_owner_allowed_information("avatar"))
)
rules.add_perm("core.view_avatar_rule", view_avatar_predicate)

# View persons groups
view_person_groups_predicate = has_person & (
    is_current_person
    | has_global_perm("core.view_person_groups")
    | has_object_perm("core.view_person_groups")
    | (is_group_owner_of_person_with_group_type & is_group_owner_allowed_information("groups"))
)
rules.add_perm("core.view_person_groups_rule", view_person_groups_predicate)

# Edit person
edit_person_predicate = has_person & (
    is_current_person & is_site_preference_set("account", "editable_fields_person")
    | has_global_perm("core.change_person")
    | has_object_perm("core.change_person")
)
rules.add_perm("core.edit_person_rule", edit_person_predicate)

# Delete person
delete_person_predicate = has_person & (
    has_global_perm("core.delete_person") | has_object_perm("core.delete_person")
)
rules.add_perm("core.delete_person_rule", delete_person_predicate)

# View groups
view_groups_predicate = has_person & (has_global_perm("core.view_group") | has_any_group)
rules.add_perm("core.view_groups_rule", view_groups_predicate)

# View group
view_group_predicate = has_person & (
    is_group_owner_with_group_type
    | has_global_perm("core.view_group")
    | has_object_perm("core.view_group")
)
rules.add_perm("core.view_group_rule", view_group_predicate)

# Edit group
edit_group_predicate = has_person & (
    has_global_perm("core.change_group") | has_object_perm("core.change_group")
)
rules.add_perm("core.edit_group_rule", edit_group_predicate)

# Delete group
delete_group_predicate = has_person & (
    has_global_perm("core.delete_group") | has_object_perm("core.delete_group")
)
rules.add_perm("core.delete_group_rule", delete_group_predicate)

# Assign child groups to groups
assign_child_groups_to_groups_predicate = has_person & has_global_perm(
    "core.assign_child_groups_to_groups"
)
rules.add_perm("core.assign_child_groups_to_groups_rule", assign_child_groups_to_groups_predicate)

# Edit school information
edit_school_information_predicate = has_person & has_global_perm("core.change_school")
rules.add_perm("core.edit_school_information_rule", edit_school_information_predicate)

# Manage data
manage_data_predicate = has_person & has_global_perm("core.manage_data")
rules.add_perm("core.manage_data_rule", manage_data_predicate)

# Mark notification as read
mark_notification_as_read_predicate = has_person & is_notification_recipient
rules.add_perm("core.mark_notification_as_read_rule", mark_notification_as_read_predicate)

# View announcements
view_announcements_predicate = has_person & (
    has_global_perm("core.view_announcement")
    | has_any_object("core.view_announcement", Announcement)
)
rules.add_perm("core.view_announcements_rule", view_announcements_predicate)

# View announcement
view_announcement_predicate = has_person & (
    has_global_perm("core.view_announcement") | has_object_perm("core.view_announcement")
)
rules.add_perm("core.view_announcement_rule", view_announcements_predicate)

# Create announcement
create_announcement_predicate = view_announcements_predicate & (
    has_global_perm("core.add_announcement")
)
rules.add_perm("core.create_announcement_rule", create_announcement_predicate)

# Edit announcement
edit_announcement_predicate = view_announcement_predicate & (
    has_global_perm("core.change_announcement") | has_object_perm("core.change_announcement")
)
rules.add_perm("core.edit_announcement_rule", edit_announcement_predicate)

# Delete announcement
delete_announcement_predicate = view_announcement_predicate & (
    has_global_perm("core.delete_announcement") | has_object_perm("core.delete_announcement")
)
rules.add_perm("core.delete_announcement_rule", delete_announcement_predicate)

# Use impersonate
impersonate_predicate = has_person & has_global_perm("core.impersonate")
rules.add_perm("core.impersonate_rule", impersonate_predicate)

# View system status
view_system_status_predicate = has_person & has_global_perm("core.view_system_status")
rules.add_perm("core.view_system_status_rule", view_system_status_predicate)

# View person personal details
view_personal_details_predicate = has_person & (
    is_current_person
    | has_global_perm("core.view_personal_details")
    | has_object_perm("core.view_personal_details")
    | (
        is_group_owner_of_person_with_group_type
        & is_group_owner_allowed_information("personal_details")
    )
)
rules.add_perm("core.view_personal_details_rule", view_personal_details_predicate)

# Change site preferences
change_site_preferences = has_person & (
    has_global_perm("core.change_site_preferences")
    | has_object_perm("core.change_site_preferences")
)
rules.add_perm("core.change_site_preferences_rule", change_site_preferences)

# Change person preferences
change_person_preferences = has_person & (
    is_current_person
    | has_global_perm("core.change_person_preferences")
    | has_object_perm("core.change_person_preferences")
)
rules.add_perm("core.change_person_preferences_rule", change_person_preferences)

# Change account preferences
change_account_preferences = has_person
rules.add_perm("core.change_account_preferences_rule", change_account_preferences)

# Change group preferences
change_group_preferences = has_person & (
    has_global_perm("core.change_group_preferences")
    | has_object_perm("core.change_group_preferences")
    | is_group_owner
)
rules.add_perm("core.change_group_preferences_rule", change_group_preferences)


# View group type
view_group_type_predicate = has_person & (
    has_global_perm("core.view_grouptype") | has_object_perm("core.view_grouptype")
)
rules.add_perm("core.view_grouptype_rule", view_group_type_predicate)

fetch_group_types_predicate = has_person
rules.add_perm("core.fetch_grouptypes_rule", fetch_group_types_predicate)

# Edit group type
change_group_type_predicate = has_person & (
    has_global_perm("core.change_grouptype") | has_object_perm("core.change_grouptype")
)
rules.add_perm("core.edit_grouptype_rule", change_group_type_predicate)

# Create group type
create_group_type_predicate = has_person & (
    has_global_perm("core.add_grouptype") | has_object_perm("core.add_grouptype")
)
rules.add_perm("core.create_grouptype_rule", create_group_type_predicate)


# Delete group type
delete_group_type_predicate = has_person & (
    has_global_perm("core.delete_grouptype") | has_object_perm("core.delete_grouptype")
)
rules.add_perm("core.delete_grouptype_rule", delete_group_type_predicate)

# View group types
view_group_types_predicate = has_person & (
    has_global_perm("core.view_grouptype") | has_any_object("core.view_grouptype", GroupType)
)
rules.add_perm("core.view_grouptypes_rule", view_group_types_predicate)

# View role
view_role_predicate = has_person & (
    has_global_perm("core.view_role") | has_object_perm("core.view_role")
)
rules.add_perm("core.view_role_rule", view_role_predicate)

fetch_roles_predicate = has_person
rules.add_perm("core.fetch_roles_rule", fetch_roles_predicate)

# Edit role
change_role_predicate = has_person & (
    has_global_perm("core.change_role") | has_object_perm("core.change_role")
)
rules.add_perm("core.edit_role_rule", change_role_predicate)

# Create role
create_role_predicate = has_person & (
    has_global_perm("core.add_role") | has_object_perm("core.add_role")
)
rules.add_perm("core.create_role_rule", create_role_predicate)

# Delete role
delete_role_predicate = has_person & (
    has_global_perm("core.delete_role") | has_object_perm("core.delete_role")
)
rules.add_perm("core.delete_role_rule", delete_role_predicate)

# View roles
view_roles_predicate = has_person & (
    has_global_perm("core.view_role") | has_any_object("core.view_role", Role)
)
rules.add_perm("core.view_roles_rule", view_roles_predicate)

# Create person
create_person_predicate = has_person & (
    has_global_perm("core.add_person") | has_object_perm("core.add_person")
)
rules.add_perm("core.create_person_rule", create_person_predicate)

# Create group
create_group_predicate = has_person & (
    has_global_perm("core.add_group") | has_object_perm("core.add_group")
)
rules.add_perm("core.create_group_rule", create_group_predicate)

# School terms
view_school_term_predicate = has_person & has_global_perm("core.view_schoolterm")
rules.add_perm("core.view_schoolterm_rule", view_school_term_predicate)

fetch_school_terms_predicate = has_person
rules.add_perm("core.fetch_schoolterms_rule", fetch_school_terms_predicate)


create_school_term_predicate = has_person & has_global_perm("core.add_schoolterm")
rules.add_perm("core.create_schoolterm_rule", create_school_term_predicate)

edit_school_term_predicate = has_person & has_global_perm("core.change_schoolterm")
rules.add_perm("core.edit_schoolterm_rule", edit_school_term_predicate)

delete_schoolterm_predicate = has_person & (
    has_global_perm("core.delete_schoolterm") | has_object_perm("core.delete_schoolterm")
)
rules.add_perm("core.delete_schoolterm_rule", delete_schoolterm_predicate)

# View group stats
view_group_stats_predicate = has_person & (
    is_group_owner_with_group_type
    | has_global_perm("core.view_group_stats")
    | has_object_perm("core.view_group_stats")
)
rules.add_perm("core.view_group_stats_rule", view_group_stats_predicate)

# View data check results
view_data_check_results_predicate = has_person & has_global_perm("core.view_datacheckresult")
rules.add_perm("core.view_datacheckresults_rule", view_data_check_results_predicate)

# Run data checks
run_data_checks_predicate = (
    has_person & view_data_check_results_predicate & has_global_perm("core.run_data_checks")
)
rules.add_perm("core.run_data_checks_rule", run_data_checks_predicate)

# Solve data problems
solve_data_problem_predicate = (
    has_person & view_data_check_results_predicate & has_global_perm("core.solve_data_problem")
)
rules.add_perm("core.solve_data_problem_rule", solve_data_problem_predicate)

view_dashboard_widget_predicate = has_person & has_global_perm("core.view_dashboardwidget")
rules.add_perm("core.view_dashboardwidget_rule", view_dashboard_widget_predicate)

create_dashboard_widget_predicate = has_person & has_global_perm("core.add_dashboardwidget")
rules.add_perm("core.create_dashboardwidget_rule", create_dashboard_widget_predicate)

edit_dashboard_widget_predicate = has_person & has_global_perm("core.change_dashboardwidget")
rules.add_perm("core.edit_dashboardwidget_rule", edit_dashboard_widget_predicate)

delete_dashboard_widget_predicate = has_person & has_global_perm("core.delete_dashboardwidget")
rules.add_perm("core.delete_dashboardwidget_rule", delete_dashboard_widget_predicate)

edit_dashboard_predicate = (
    is_site_preference_set("general", "dashboard_editing") & has_person & ~is_dummy
)
rules.add_perm("core.edit_dashboard_rule", edit_dashboard_predicate)

view_dashboardwidgets_predicate = edit_dashboard_predicate
rules.add_perm("core.view_dashboardwidgets_rule", view_dashboardwidgets_predicate)

edit_default_dashboard_predicate = has_person & has_global_perm("core.edit_default_dashboard")
rules.add_perm("core.edit_default_dashboard_rule", edit_default_dashboard_predicate)

delete_dashboard_widget_instance_predicate = edit_default_dashboard_predicate | (
    edit_dashboard_predicate & is_dashboard_widget_instance_owner
)
rules.add_perm(
    "core.delete_dashboard_widget_instance_rule", delete_dashboard_widget_instance_predicate
)

# django-invitations
invite_enabled_predicate = is_site_preference_set(section="auth", pref="invite_enabled")
rules.add_perm("core.invite_enabled", invite_enabled_predicate)

accept_invite_predicate = has_person & invite_enabled_predicate
rules.add_perm("core.accept_invite_rule", accept_invite_predicate)

invite_predicate = has_person & invite_enabled_predicate & has_global_perm("core.invite")
rules.add_perm("core.invite_rule", invite_predicate)

# django-allauth
signup_enabled_predicate = is_site_preference_set(section="auth", pref="signup_enabled")
rules.add_perm("core.signup_rule", signup_enabled_predicate)

signup_menu_predicate = signup_enabled_predicate | invite_enabled_predicate
rules.add_perm("core.signup_menu_rule", signup_menu_predicate)

change_password_predicate = has_person & is_site_preference_set(
    section="auth", pref="allow_password_change"
)
rules.add_perm("core.change_password_rule", change_password_predicate)

change_person_user_password_predicate = (
    view_person_predicate
    & has_person_user
    & (has_global_perm("core.change_user_password") | has_object_perm("core.change_user_password"))
)
rules.add_perm(
    "core.change_user_password_rule",
    change_person_user_password_predicate,
)

reset_person_user_password_predicate = (
    view_person_predicate
    & has_person_user
    & has_person_email
    & (
        has_global_perm("core.reset_user_password")
        | has_object_perm("core.reset_user_password")
        | (is_site_preference_set(section="auth", pref="allow_password_reset") & is_current_person)
    )
)
rules.add_perm("core.reset_user_password_rule", reset_person_user_password_predicate)

reset_password_predicate = is_site_preference_set(section="auth", pref="allow_password_reset")
rules.add_perm("core.reset_password_rule", reset_password_predicate)

# OAuth2 permissions
view_oauthapplication_predicate = has_person & has_global_perm("core.view_oauthapplication")
rules.add_perm("core.view_oauthapplication_rule", view_oauthapplication_predicate)

rules.add_perm("core.view_oauthapplications_rule", view_oauthapplication_predicate)

create_oauthapplication_predicate = has_person & has_global_perm("core.add_oauthapplication")
rules.add_perm("core.create_oauthapplication_rule", create_oauthapplication_predicate)

delete_oauthapplication_predicate = has_person & has_global_perm("core.delete_oauthapplication")
rules.add_perm("core.delete_oauthapplication_rule", delete_oauthapplication_predicate)

edit_oauthapplication_predicate = has_person & has_global_perm("core.change_oauthapplication")
rules.add_perm("core.edit_oauthapplication_rule", edit_oauthapplication_predicate)

# View admin menu
view_admin_menu_predicate = has_person & (
    manage_data_predicate
    | impersonate_predicate
    | view_system_status_predicate
    | view_data_check_results_predicate
    | view_oauthapplication_predicate
    | view_dashboard_widget_predicate
)
rules.add_perm("core.view_admin_menu_rule", view_admin_menu_predicate)

# Upload and browse files via CKEditor
upload_files_ckeditor_predicate = has_person & has_global_perm("core.upload_files_ckeditor")
rules.add_perm("core.upload_files_ckeditor_rule", upload_files_ckeditor_predicate)

manage_person_permissions_predicate = has_person & is_superuser
rules.add_perm("core.manage_permissions_rule", manage_person_permissions_predicate)

test_pdf_generation_predicate = has_person & has_global_perm("core.test_pdf")
rules.add_perm("core.test_pdf_rule", test_pdf_generation_predicate)

view_progress_predicate = has_person & is_own_celery_task
rules.add_perm("core.view_progress_rule", view_progress_predicate)

view_calendar_feed_predicate = has_person
rules.add_perm("core.view_calendar_feed_rule", view_calendar_feed_predicate)

# Holidays

view_holiday_predicate = has_person & (
    has_global_perm("core.view_holiday") | has_object_perm("core.view_holiday")
)
rules.add_perm("core.view_holiday_rule", view_holiday_predicate)

view_holidays_predicate = has_person & (
    has_global_perm("core.view_holiday") | has_any_object("core.view_holiday", Holiday)
)
rules.add_perm("core.view_holidays_rule", view_holidays_predicate)

edit_holiday_predicate = has_person & (
    has_global_perm("core.change_holiday") | has_object_perm("core.change_holiday")
)
rules.add_perm("core.edit_holiday_rule", edit_holiday_predicate)

create_holiday_predicate = has_person & (has_global_perm("core.add_holiday"))
rules.add_perm("core.create_holiday_rule", create_holiday_predicate)

delete_holiday_predicate = has_person & (
    has_global_perm("core.delete_holiday") | has_object_perm("core.delete_holiday")
)
rules.add_perm("core.delete_holiday_rule", delete_holiday_predicate)

# Availability events

view_availability_events_predicate = has_person & (
    has_global_perm("core.view_availabilityevent")
    | has_any_object("core.view_availabilityevent", AvailabilityEvent)
)
rules.add_perm("core.view_availability_events_rule", view_availability_events_predicate)

view_own_availability_events_predicate = has_person
rules.add_perm("core.view_own_availability_events_rule", view_own_availability_events_predicate)

create_availability_event_predicate = has_person
rules.add_perm("core.create_availability_event_rule", create_availability_event_predicate)

edit_availability_event_predicate = has_person & (
    has_global_perm("core.change_availabilityevent")
    | is_own_availability_event
    | has_object_perm("core.change_availabilityevent")
)
rules.add_perm("core.edit_availability_event_rule", edit_availability_event_predicate)

delete_availability_event_predicate = has_person & (
    has_global_perm("core.delete_availabilityevent")
    | is_own_availability_event
    | has_object_perm("core.delete_availabilityevent")
)
rules.add_perm("core.delete_availability_event_rule", delete_availability_event_predicate)

# Availability types

view_public_availability_types_predicate = has_person
rules.add_perm("core.view_public_availability_types_rule", view_public_availability_types_predicate)

view_all_availability_types_predicate = has_person & (has_global_perm("core.view_availabilitytype"))
rules.add_perm("core.view_all_availability_types_rule", view_all_availability_types_predicate)

create_availability_type_predicate = has_person & (has_global_perm("core.add_availabilitytype"))
rules.add_perm("core.create_availability_type_rule", create_availability_type_predicate)

edit_availability_type_predicate = has_person & (
    has_global_perm("core.change_availabilitytype")
    | has_object_perm("core.change_availabilitytype")
)
rules.add_perm("core.edit_availability_type_rule", edit_availability_type_predicate)

delete_availability_type_predicate = has_person & (
    has_global_perm("core.delete_availabilitytype")
    | has_object_perm("core.delete_availabilitytype")
)
rules.add_perm("core.delete_availability_type_rule", delete_availability_type_predicate)

# Aggregated free/busy feed

view_person_free_busy_feed = has_person & (
    is_current_person
    | has_global_perm("core.view_person_free_busy_feed")
    | has_object_perm("core.view_person_free_busy_feed")
)
rules.add_perm("core.view_person_free_busy_feed_rule", view_person_free_busy_feed)

view_group_free_busy_feed = has_person & (
    is_group_owner
    | has_global_perm("core.view_group_free_busy_feed")
    | has_object_perm("core.view_group_free_busy_feed")
)
rules.add_perm("core.view_group_free_busy_feed_rule", view_group_free_busy_feed)

view_free_busy_predicate = has_person
rules.add_perm("core.view_free_busy_rule", view_free_busy_predicate)

# View people menu (persons + objects)
rules.add_perm(
    "core.view_people_menu_rule",
    has_person
    & (
        view_persons_predicate
        | view_groups_predicate
        | assign_child_groups_to_groups_predicate
        | view_own_availability_events_predicate
    ),
)

# Custom events

create_personal_event_predicate = has_person
rules.add_perm("core.create_personal_event_rule", create_personal_event_predicate)

create_personal_event_with_invitations_predicate = has_person & has_global_perm(
    "core.add_personalevent"
)
rules.add_perm(
    "core.create_personal_event_with_invitations_rule",
    create_personal_event_with_invitations_predicate,
)

edit_personal_event_predicate = has_person & (
    has_global_perm("core.change_personalevent") | is_personal_event_owner
)
rules.add_perm("core.edit_personal_event_rule", edit_personal_event_predicate)

delete_personal_event_predicate = has_person & (
    has_global_perm("core.delete_personalevent") | is_personal_event_owner
)
rules.add_perm("core.delete_personal_event_rule", delete_personal_event_predicate)

# Personal todos

create_personaltodo_predicate = has_person
rules.add_perm("core.create_personaltodo_rule", create_personaltodo_predicate)

create_personaltodo_with_invitations_predicate = has_person & has_global_perm(
    "core.add_personaltodo"
)
rules.add_perm(
    "core.create_personaltodo_with_invitations_rule",
    create_personaltodo_with_invitations_predicate,
)

edit_personaltodo_predicate = has_person & (
    has_global_perm("core.change_personaltodo") | is_personal_todo_owner
)
rules.add_perm("core.edit_personaltodo_rule", edit_personaltodo_predicate)

delete_personaltodo_predicate = has_person & (
    has_global_perm("core.delete_personaltodo") | is_personal_todo_owner
)
rules.add_perm("core.delete_personaltodo_rule", delete_personaltodo_predicate)

# Rooms
view_room_predicate = has_person & (
    has_global_perm("core.view_room") | has_object_perm("core.view_room")
)
rules.add_perm("core.view_room_rule", view_room_predicate)

view_rooms_predicate = has_person & (
    has_global_perm("core.view_room") | has_any_object("core.view_room", Room)
)
rules.add_perm("core.view_rooms_rule", view_rooms_predicate)

edit_room_predicate = has_person & (
    has_global_perm("core.change_room") | has_object_perm("core.change_room")
)
rules.add_perm("core.edit_room_rule", edit_room_predicate)

create_room_predicate = has_person & (has_global_perm("core.add_room"))
rules.add_perm("core.create_room_rule", create_room_predicate)

delete_room_predicate = has_person & (
    has_global_perm("core.delete_room") | has_object_perm("core.delete_room")
)
rules.add_perm("core.delete_room_rule", delete_room_predicate)

# Organisations
view_organisation_predicate = has_person & (
    has_global_perm("core.view_organisation") | has_object_perm("core.view_organisation")
)
rules.add_perm("core.view_organisation_rule", view_organisation_predicate)

view_organisations_predicate = has_person & (
    has_global_perm("core.view_organisation")
    | has_any_object("core.view_organisation", Organisation)
)
rules.add_perm("core.view_organisations_rule", view_organisations_predicate)

edit_organisation_predicate = has_person & (
    has_global_perm("core.change_organisation") | has_object_perm("core.change_organisation")
)
rules.add_perm("core.edit_organisation_rule", edit_organisation_predicate)

create_organisation_predicate = has_person & (has_global_perm("core.add_organisation"))
rules.add_perm("core.create_organisation_rule", create_organisation_predicate)

delete_organisation_predicate = has_person & (
    has_global_perm("core.delete_organisation") | has_object_perm("core.delete_organisation")
)
rules.add_perm("core.delete_organisation_rule", delete_organisation_predicate)

view_data_management_menu_predicate = has_person & (
    manage_data_predicate
    | view_school_term_predicate
    | view_announcements_predicate
    | view_holidays_predicate
    | view_room_predicate
)
rules.add_perm("core.view_data_management_menu_rule", view_data_management_menu_predicate)

# Maintenance mode
set_maintenance_mode_predicate = has_person & is_superuser
rules.add_perm("core.set_maintenance_mode_rule", set_maintenance_mode_predicate)
