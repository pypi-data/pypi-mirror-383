import { ref } from "vue";
import { useQuery } from "../app/apollo";
import gqlCustomMenu from "../../components/app/customMenu.graphql";

export function useFooterMenu() {
  const footerMenu = ref(null);

  const { onResult } = useQuery(gqlCustomMenu, () => ({
    name: "footer",
  }));

  onResult(({ data }) => {
    footerMenu.value = data.customMenuByName;
  });

  return {
    footerMenu,
  };
}
