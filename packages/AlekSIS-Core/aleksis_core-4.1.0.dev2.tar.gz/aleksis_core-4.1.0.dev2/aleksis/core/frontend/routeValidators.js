/**
 * Check whether the user is logged in on the AlekSIS server.
 *
 * @param {Object} whoAmI The person object as returned by the whoAmI query
 * @returns true if the user is logged in, false if not
 */
const notLoggedInValidator = (whoAmI) => {
  return !whoAmI || whoAmI.isAnonymous;
};

const hasPersonValidator = (whoAmI) => {
  return whoAmI && whoAmI.person && !whoAmI.person.isDummy;
};

/**
 * Check whether invites are enabled.
 *
 * @param {Object} systemProperties object as returned by the systemProperties query
 * @returns true if invites are enabled and false otherwise
 */
const inviteEnabledValidator = (_, systemProperties) => {
  return systemProperties && systemProperties.sitePreferences.inviteEnabled;
};

/**
 * Check whether signup is enabled.
 *
 * @param {Object} systemProperties object as returned by the systemProperties query
 * @returns true if invites are enabled and false otherwise
 */
const signupEnabledValidator = (_, systemProperties) => {
  return systemProperties && systemProperties.sitePreferences.signupEnabled;
};

export {
  notLoggedInValidator,
  hasPersonValidator,
  inviteEnabledValidator,
  signupEnabledValidator,
};
