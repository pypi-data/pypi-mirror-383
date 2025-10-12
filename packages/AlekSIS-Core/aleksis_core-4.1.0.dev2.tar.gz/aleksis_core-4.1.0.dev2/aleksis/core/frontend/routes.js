/*
 * Vue router definitions for all of AlekSIS.
 *
 * This module defines the routes of AlekSIS-Core and also loads
 * and adds all routes from known apps.
 */

// aleksisAppImporter is a virtual module defined in Vite config
import { appRoutes } from "aleksisAppImporter";

import { notLoggedInValidator } from "./routeValidators";

const routes = [
  {
    path: "/accounts/login/",
    name: "core.accounts.login",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    meta: {
      inMenu: true,
      order: 10,
      parent: true,
      icon: "mdi-login-variant",
      titleKey: "accounts.login.menu_title",
      validators: [notLoggedInValidator],
      invalidate: "leave",
    },
  },
  {
    path: "/accounts/reauthenticate/",
    name: "core.accounts.reauthenticate",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
  },
  {
    path: "/accounts/2fa/authenticate",
    name: "core.accounts.2faAuthenticate",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
  },
  {
    path: "/accounts/2fa/recovery-codes/download",
    name: "core.accounts.downloadRecoveryCodes",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
  },
  {
    path: "/accounts/signup/",
    name: "core.accounts.signup",
    component: () => import("./components/account/AccountRegistrationForm.vue"),
    meta: {
      inMenu: true,
      parent: true,
      order: 11,
      icon: "mdi-account-plus-outline",
      iconActive: "mdi-account-plus",
      titleKey: "accounts.signup.menu_title",
      validators: [notLoggedInValidator],
      permission: "core.signup_menu_rule",
      invalidate: "leave",
    },
  },
  {
    path: "/",
    name: "dashboard",
    component: () => import("./components/dashboard/WrappedDashboard.vue"),
    meta: {
      inMenu: true,
      parent: true,
      order: 20,
      icon: "$home",
      iconActive: "mdi-home",
      titleKey: "dashboard.menu_title",
      permission: "core.view_dashboard_rule",
      exact: true,
      fullWidth: true,
    },
  },
  {
    path: "/calendar/",
    component: () => import("./components/calendar/CalendarOverview.vue"),
    name: "core.calendar_overview",
    meta: {
      inMenu: true,
      order: 30,
      icon: "mdi-calendar-outline",
      iconActive: "mdi-calendar",
      titleKey: "calendar.menu_title",
      toolbarTitle: "calendar.menu_title",
      permission: "core.view_calendar_feed_rule",
    },
    children: [
      {
        path: ":view(month|week|day)/:year(\\d\\d\\d\\d)/:month(\\d\\d?)/:day(\\d\\d?)/",
        component: () => import("./components/calendar/CalendarOverview.vue"),
        name: "core.calendar_overview_with_params",
        meta: {
          titleKey: "calendar.menu_title",
          toolbarTitle: "calendar.menu_title",
          permission: "core.view_calendar_feed_rule",
        },
      },
    ],
  },
  {
    path: "/people",
    name: "core.people",
    meta: {
      inMenu: true,
      order: 40,
      titleKey: "people",
      icon: "mdi-account-group-outline",
      iconActive: "mdi-account-group",
      permission: "core.view_people_menu_rule",
    },
    children: [
      {
        path: "/o/core/person/",
        component: () => import("./components/person/PersonListWrapper.vue"),
        name: "core.persons",
        meta: {
          inMenu: true,
          order: 10,
          titleKey: "person.menu_title",
          icon: "mdi-account-outline",
          iconActive: "mdi-account",
          permission: "core.view_persons_rule",
        },
      },
      {
        path: "/o/core/person/:id(\\d+)",
        component: () =>
          import("./components/person/PersonOverviewWrapper.vue"),
        name: "core.personById",
        props: true,
        meta: {
          titleKey: "person.page_title",
          permission: "core.view_persons_rule",
        },
      },
      {
        path: "/o/core/person/:id(\\d+)/invite/",
        component: () => import("./components/LegacyBaseTemplate.vue"),
        props: {
          byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
        },
        name: "core.invitePerson",
        meta: {
          titleKey: "person.invite",
          permission: "core.invite_rule",
        },
      },
      {
        path: "/o/core/group/",
        component: () => import("./components/group/GroupList.vue"),
        name: "core.groups",
        meta: {
          inMenu: true,
          order: 20,
          titleKey: "group.menu_title",
          icon: "mdi-account-multiple-outline",
          iconActive: "mdi-account-multiple",
          permission: "core.view_groups_rule",
        },
      },
      {
        path: "/o/core/group/create",
        component: () => import("./components/LegacyBaseTemplate.vue"),
        props: {
          byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
        },
        name: "core.createGroup",
      },
      {
        path: "/o/core/group/:id(\\d+)",
        component: () => import("./components/group/GroupOverview.vue"),
        props: true,
        name: "core.group",
        meta: {
          permission: "core.view_groups_rule",
        },
      },
      {
        path: "/o/core/group/:id(\\d+)/edit",
        component: () => import("./components/LegacyBaseTemplate.vue"),
        props: {
          byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
        },
        name: "core.editGroup",
      },
      {
        path: "/o/core/group_type/",
        component: () => import("./components/group_type/GroupType.vue"),
        name: "core.groupTypes",
        meta: {
          inMenu: true,
          order: 30,
          titleKey: "group_type.menu_title",
          icon: "$groupType",
          iconActive: "mdi-shape",
          permission: "core.view_grouptypes_rule",
        },
      },
      {
        path: "/o/core/role/",
        component: () => import("./components/role/Role.vue"),
        name: "core.roles",
        meta: {
          inMenu: true,
          order: 40,
          titleKey: "role.menu_title",
          icon: "$role",
          iconActive: "mdi-badge-account-horizontal",
          permission: "core.view_roles_rule",
        },
      },
      {
        path: "/invitations/send-invite",
        component: () => import("./components/LegacyBaseTemplate.vue"),
        props: {
          byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
        },
        name: "core.invite_person",
      },
      {
        path: "/availability_events/",
        component: () =>
          import("./components/availability_event/AvailabilityEventList.vue"),
        name: "core.availability_events",
        meta: {
          inMenu: true,
          order: 50,
          titleKey: "availability_event.menu_title",
          toolbarTitle: "availability_event.menu_title",
          icon: "mdi-calendar-check-outline",
          permission: "core.view_own_availability_events_rule",
        },
      },
      {
        path: "/free_busy/",
        component: () => import("./components/free_busy/FreeBusyOverview.vue"),
        name: "core.overview_free_busy",
        meta: {
          inMenu: true,
          order: 60,
          titleKey: "free_busy.overview.menu_title",
          toolbarTitle: "free_busy.overview.menu_title",
          icon: "mdi-calendar-multiple-check",
          permission: "core.view_free_busy_rule",
        },
      },
    ],
  },
  {
    path: "/data_management",
    name: "core.data_management",
    meta: {
      inMenu: true,
      order: 50,
      titleKey: "data_management",
      icon: "mdi-application-cog-outline",
      iconActive: "mdi-application-cog",
      permission: "core.view_data_management_menu_rule",
    },
    children: [
      {
        path: "/o/core/room/",
        component: () => import("./components/room/RoomInlineList.vue"),
        name: "core.rooms",
        meta: {
          inMenu: true,
          order: 10,
          titleKey: "room.menu_title",
          toolbarTitle: "room.menu_title",
          icon: "mdi-floor-plan",
          permission: "core.view_rooms_rule",
        },
      },
      {
        path: "/o/core/announcement/",
        component: () => import("./components/announcements/Announcements.vue"),
        name: "core.announcements",
        meta: {
          inMenu: true,
          order: 20,
          titleKey: "announcement.menu_title",
          icon: "mdi-message-alert-outline",
          iconActive: "mdi-message-alert",
          permission: "core.view_announcements_rule",
        },
      },
      {
        path: "/o/core/holiday/",
        component: () => import("./components/holiday/HolidayInlineList.vue"),
        name: "core.holidays",
        meta: {
          inMenu: true,
          order: 30,
          titleKey: "holiday.menu_title",
          icon: "$holidays",
          iconActive: "mdi-calendar-weekend",
          permission: "core.view_holidays_rule",
        },
      },
      {
        path: "/o/core/school_term/",
        component: () =>
          import("./components/school_term/SchoolTermInlineList.vue"),
        name: "core.school_terms",
        meta: {
          inMenu: true,
          order: 40,
          titleKey: "school_term.menu_title",
          icon: "$schoolTerm",
          iconActive: "mdi-calendar-range",
          permission: "core.view_schoolterm_rule",
        },
      },
      {
        path: "/o/core/availability_type/",
        component: () =>
          import("./components/availability_type/AvailabilityTypeList.vue"),
        name: "core.availability_types",
        meta: {
          inMenu: true,
          order: 50,
          titleKey: "availability_type.menu_title",
          toolbarTitle: "availability_type.menu_title",
          icon: "mdi-calendar-multiple-check",
          permission: "core.view_all_availability_types_rule",
        },
      },
    ],
  },
  {
    path: "/admin",
    name: "core.administration",
    meta: {
      inMenu: true,
      order: 60,
      titleKey: "administration.menu_title",
      icon: "mdi-security",
      permission: "core.view_admin_menu_rule",
    },
    children: [
      {
        path: "/dashboard_widgets/",
        component: () =>
          import(
            "./components/dashboard_widget/management/DashboardWidgetManagementList.vue"
          ),
        name: "core.dashboardWidgets",
        meta: {
          inMenu: true,
          order: 10,
          titleKey: "dashboard.dashboard_widget.menu_title",
          icon: "mdi-view-dashboard-outline",
          iconActive: "mdi-view-dashboard",
          permission: "core.view_dashboardwidget_rule",
        },
      },
      {
        path: "/dashboard_widgets/default",
        component: () =>
          import("./components/dashboard/management/ManageDashboard.vue"),
        props: {
          defaultDashboard: true,
        },
        name: "core.editDefaultDashboard",
        meta: {
          permission: "core.edit_default_dashboard_rule",
        },
      },
      {
        path: "/status/",
        component: () => import("./components/system_status/SystemStatus.vue"),
        name: "core.system_status",
        meta: {
          inMenu: true,
          order: 20,
          titleKey: "administration.system_status.menu_title",
          toolbarTitle: "administration.system_status.menu_title",
          icon: "mdi-power-settings",
          permission: "core.view_system_status_rule",
        },
      },
      {
        path: "/preferences/site/",
        component: () => import("./components/LegacyBaseTemplate.vue"),
        props: {
          byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
        },
        name: "core.preferencesSite",
        meta: {
          inMenu: true,
          order: 30,
          titleKey: "preferences.site.menu_title",
          icon: "mdi-tune",
          permission: "core.change_site_preferences_rule",
        },
      },
      {
        path: "/preferences/site/:section/",
        component: () => import("./components/LegacyBaseTemplate.vue"),
        props: {
          byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
        },
        name: "core.preferencesSiteSection",
      },
      {
        path: "/data_checks/",
        component: () => import("./components/data_check/DataCheck.vue"),
        name: "core.checkData",
        meta: {
          inMenu: true,
          order: 40,
          titleKey: "administration.data_check.menu_title",
          toolbarTitle: "administration.data_check.menu_title",
          icon: "mdi-list-status",
          permission: "core.view_datacheckresults_rule",
        },
      },
      {
        path: "/data_checks/run/",
        component: () => import("./components/LegacyBaseTemplate.vue"),
        props: {
          byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
        },
        name: "core.runDataChecks",
      },
      {
        path: "/data_checks/:pk(\\d+)/:solve_option/",
        component: () => import("./components/LegacyBaseTemplate.vue"),
        props: {
          byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
        },
        name: "core.solveDataCheck",
      },

      {
        path: "/permissions/global/user/",
        component: () => import("./components/LegacyBaseTemplate.vue"),
        props: {
          byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
        },
        name: "core.managerUserGlobalPermissions",
        meta: {
          inMenu: true,
          order: 50,
          titleKey: "permissions.manage.menu_title",
          icon: "mdi-shield-outline",
          iconActive: "mdi-shield",
          permission: "core.manage_permissions_rule",
        },
      },
      {
        path: "/permissions/global/group/",
        component: () => import("./components/LegacyBaseTemplate.vue"),
        props: {
          byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
        },
        name: "core.manageGroupGlobalPermissions",
      },
      {
        path: "/permissions/object/user/",
        component: () => import("./components/LegacyBaseTemplate.vue"),
        props: {
          byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
        },
        name: "core.manageUserObjectPermissions",
      },
      {
        path: "/permissions/object/group/",
        component: () => import("./components/LegacyBaseTemplate.vue"),
        props: {
          byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
        },
        name: "core.manageGroupObjectPermissions",
      },
      {
        path: "/permissions/global/user/:pk(\\d+)/delete/",
        component: () => import("./components/LegacyBaseTemplate.vue"),
        props: {
          byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
        },
        name: "core.deleteUserGlobalPermission,",
      },
      {
        path: "/permissions/global/group/:pk(\\d+)/delete/",
        component: () => import("./components/LegacyBaseTemplate.vue"),
        props: {
          byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
        },
        name: "core.deleteGroupGlobalPermission",
      },
      {
        path: "/permissions/object/user/:pk(\\d+)/delete/",
        component: () => import("./components/LegacyBaseTemplate.vue"),
        props: {
          byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
        },
        name: "core.deleteUserObjectPermission",
      },
      {
        path: "/permissions/object/group/:pk(\\d+)/delete/",
        component: () => import("./components/LegacyBaseTemplate.vue"),
        props: {
          byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
        },
        name: "core.deleteGroupObjectPermission",
      },
      {
        path: "/permissions/assign/",
        component: () => import("./components/LegacyBaseTemplate.vue"),
        props: {
          byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
        },
        name: "core.selectPermissionforAssign",
      },
      {
        path: "/permissions/:pk(\\d+)/assign/",
        component: () => import("./components/LegacyBaseTemplate.vue"),
        props: {
          byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
        },
        name: "core.assignPermission",
      },
      {
        path: "/oauth/applications/",
        component: () => import("./components/oauth/OAuthApplications.vue"),
        name: "core.oauthApplications",
        meta: {
          inMenu: true,
          order: 60,
          titleKey: "o_auth_application.menu_title",
          toolbarTitle: "o_auth_application.menu_title",
          icon: "mdi-gesture-tap-hold",
          permission: "core.view_oauthapplications_rule",
        },
      },
    ],
  },
  {
    path: "/impersonate/:uid(\\d+)",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "impersonate.impersonateByUserPk",
    meta: {
      invalidate: "leave",
    },
  },

  // ACCOUNT MENU

  {
    path: "/impersonate/stop/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "impersonate.stop",
    meta: {
      invalidate: "leave",
    },
  },
  {
    path: "/o/",
    component: () => import("./components/person/PersonOverview.vue"),
    name: "core.me",
    meta: {
      inAccountMenu: true,
      parent: true,
      titleKey: "person.account_menu_title",
      icon: "mdi-account-outline",
      iconActive: "mdi-account",
      permission: "core.view_account_rule",
    },
  },
  {
    path: "/preferences/person/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.preferencesPerson",
    meta: {
      inAccountMenu: true,
      parent: true,
      titleKey: "preferences.person.menu_title",
      icon: "$preferences",
      permission: "core.change_account_preferences_rule",
    },
  },
  {
    path: "/preferences/person/:pk(\\d+)/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.preferencesPersonByPk",
  },
  {
    path: "/preferences/person/:pk(\\d+)/:section/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.preferencesPersonByPkSection",
  },
  {
    path: "/preferences/person/:section/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.preferencesPersonSection",
  },
  {
    path: "/accounts/2fa/",
    component: () => import("./components/two_factor/TwoFactor.vue"),
    name: "core.twoFactor",
    meta: {
      inAccountMenu: true,
      parent: true,
      titleKey: "accounts.two_factor.menu_title",
      toolbarTitle: "accounts.two_factor.title",
      icon: "mdi-two-factor-authentication",
      permission: "core.manage_2fa_rule",
    },
  },
  {
    path: "/accounts/password/change/",
    redirect: { name: "core.me", query: { _ui_action: "change_password" } },
    name: "core.accounts.changePassword",
    meta: {
      inAccountMenu: true,
      parent: true,
      titleKey: "accounts.change_password.menu_title",
      icon: "mdi-form-textbox-password",
      permission: "core.change_password_rule",
    },
  },
  {
    path: "/accounts/password/reset/",
    component: () => import("./components/account/ResetPassword.vue"),
    name: "core.accounts.resetPassword",
    meta: {
      titleKey: "accounts.reset_password.title",
      toolbarTitle: "accounts.reset_password.title",
      permission: "core.reset_password_rule",
    },
  },
  {
    path: "/accounts/password/reset/done/",
    component: () => import("./components/account/ResetPasswordDone.vue"),
    name: "core.accounts.resetPasswordDone",
    meta: {
      titleKey: "accounts.reset_password.title",
      toolbarTitle: "accounts.reset_password.title",
      permission: "core.reset_password_rule",
    },
  },
  {
    path: "/accounts/password/reset/key/:resetKey/",
    component: () => import("./components/account/ResetPasswordFromKey.vue"),
    props: true,
    name: "core.accounts.resetPasswordConfirm",
    meta: {
      titleKey: "accounts.reset_password.title",
      toolbarTitle: "accounts.reset_password.title",
    },
  },
  {
    path: "/accounts/inactive/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.accounts.inactive",
  },
  {
    path: "/accounts/email/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.accounts.email",
  },
  {
    path: "/accounts/confirm-email/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.accounts.confirmEmail",
  },
  {
    path: "/accounts/confirm-email/:key/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.accounts.confirmEmailKey",
  },
  {
    path: "/accounts/3rdparty/login/cancelled/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.accounts.socialLoginCancelled",
  },
  {
    path: "/accounts/3rdparty/login/error/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.accounts.socialLoginError",
  },
  {
    path: "/accounts/3rdparty/signup/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.accounts.socialSignup",
  },
  {
    path: "/accounts/3rdparty/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.accounts.socialConnections",
    meta: {
      inAccountMenu: true,
      parent: true,
      titleKey: "accounts.social_connections.menu_title",
      icon: "mdi-earth",
      permission: "core.manage_social_connections_rule",
    },
  },
  {
    path: "/accounts/3rdparty/:pk(\\d+)/delete",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.accounts.deleteSocialConnection",
  },
  {
    path: "/oauth/authorized_tokens/",
    component: () =>
      import(
        "./components/authorized_oauth_applications/AuthorizedApplications.vue"
      ),
    name: "core.oauth.authorizedTokens",
    meta: {
      inAccountMenu: true,
      parent: true,
      titleKey: "oauth.authorized_application.menu_title",
      toolbarTitle: "oauth.authorized_application.title",
      icon: "mdi-gesture-tap-hold",
      permission: "core.manage_authorized_tokens_rule",
    },
  },
  {
    path: "/oauth/authorized_tokens/:pk(\\d+)/delete/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.oauth.deleteAuthorizedToken",
  },
  {
    path: "/accounts/logout/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.accounts.logout",
    meta: {
      inAccountMenu: true,
      parent: true,
      titleKey: "accounts.logout.menu_title",
      icon: "mdi-logout-variant",
      permission: "core.logout_rule",
      divider: true,
      invalidate: "leave",
    },
  },
  {
    path: "/invitations/code/generate",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.generate_invitation_code",
  },
  {
    path: "/invitations/disabled",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.invite_disabled",
  },
  {
    path: "/preferences/group/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.preferencesGroup",
  },
  {
    path: "/preferences/group/:pk(\\d+)/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.preferencesGroupByPk",
  },
  {
    path: "/preferences/group/:pk(\\d+)/:section/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.preferencesGroupByPkSection",
  },
  {
    path: "/preferences/group/:section/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.preferencesGroupSection",
  },
  {
    path: "/health/pdf/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.testPdf",
  },
  {
    path: "/pdfs/:id",
    component: () => import("./components/pdf/DownloadPDF.vue"),
    name: "core.redirectToPdfUrl",
  },
  {
    path: "/search/",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "core.haystack_search",
  },
  {
    path: "/celery_progress/:id",
    component: () => import("./components/celery_progress/CeleryProgress.vue"),
    props: true,
    name: "core.celery_progress",
  },
  {
    path: "/about",
    component: () => import("./components/about/About.vue"),
    name: "core.about",
    meta: {
      titleKey: "about.page_title",
    },
  },
  {
    path: "/invitations/accept-invite/:code",
    component: () => import("./components/LegacyBaseTemplate.vue"),
    props: {
      byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
    },
    name: "invitations.accept_invite",
  },
];

// This imports all known AlekSIS app entrypoints
// The list is generated by util/frontent_helpers.py and passed to Vite,
//  which aliases the app package names into virtual JavaScript modules
//  and generates importing code at bundle time.
for (const [appName, appRoute] of Object.entries(appRoutes)) {
  routes.push({
    path: `/o/${appName}`,
    name: `objects.${appName}`,
    children: appRoute.object,
  });

  routes.push({
    ...appRoute.default,
    path: `/app/${appName}`,
    name: `${appName}`,
  });
}

export default routes;
