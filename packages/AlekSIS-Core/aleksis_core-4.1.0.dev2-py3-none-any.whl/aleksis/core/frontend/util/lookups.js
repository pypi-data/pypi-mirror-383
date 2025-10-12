/**
 * Lookup nested key
 * Keys are either an array of string keys or one string with . seperated keys.
 *
 * @param {string | string[]} keys Dot-separated key or array of keys.
 * @param {Record<string, any>} object Object to do the recursive lookup on.
 * @returns {any} The value of the nested key
 */
export function getKeysRecursive(keys, object) {
  if (Array.isArray(keys)) {
    return keys.reduce((obj, key) => obj[key], object);
  }
  if (typeof keys === "string") {
    return getKeysRecursive(keys.split("."), object);
  } else {
    console.error("Expeced array or string got:", keys);
  }
}

/**
 * Set nested key
 * Keys are either an array of string keys or one string with . seperated keys.
 *
 * @param {string | string[]} keys Dot-separated key or array of keys.
 * @param {Record<string, any>} object Object to do the recursive set on.
 * @param {any} value Value to set.
 * @returns {any} The new value of the nested key
 */
export function setKeysRecursive(keys, object, value) {
  if (Array.isArray(keys)) {
    const [first, ...rest] = keys;
    if (rest.length === 0) {
      return (object[first] = value);
    } else {
      return setKeysRecursive(rest, object[first], value);
    }
  }
  if (typeof keys === "string") {
    return setKeysRecursive(keys.split("."), object, value);
  } else {
    console.error("Expected array or string got:", keys);
  }
}

/**
 * Get object title by object value and looking up from choices.
 *
 * @param {Record<string, any>[]} choices List of choices
 * @param {any} value Value to look up the title for
 * @param {string} valueKey Key for object value
 * @param {string} titleKey Key for title value
 */
export function lookupChoiceTitle(
  choices,
  value,
  valueKey = "value",
  titleKey = "title",
) {
  return (choices.find((choice) => choice[valueKey] === value) || {
    [titleKey]: value,
  })[titleKey];
}
