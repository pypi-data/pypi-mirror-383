import {
  deletePersons,
  persons,
} from "../components/person/personList.graphql";
import {
  createPersons,
  updatePersons,
} from "../components/person/personForm.graphql";

export default {
  data() {
    return {
      i18nKey: "person",
      gqlQuery: persons,
      gqlDeleteMutation: deletePersons,
      gqlCreateMutation: createPersons,
      gqlPatchMutation: updatePersons,
    };
  },
};
