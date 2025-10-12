<script>
import { defineComponent, h } from "vue";

export default defineComponent({
  props: {
    // { slot, component, props }
    field: {
      type: Object,
      required: true,
    },
  },
  setup(props, { attrs }) {
    if (props.field.slot) {
      // TODO: Simplify this nested if
      // For some reason modelValue passed via field.props needs to be separate here. It is the same in vjsf.
      if (props.field.props.modelValue) {
        return () =>
          h(
            "div",
            props.field.slot({
              ...attrs,
              ...props.field.props,
              modelValue: props.field.props.modelValue.value,
            }),
          );
      } else {
        return () =>
          h("div", props.field.slot({ ...attrs, ...props.field.props }));
      }
    } else {
      // For some reason modelValue passed via field.props needs to be separate here. It is the same in vjsf.
      if (props.field.props.modelValue) {
        return () =>
          h(props.field.component, {
            ...attrs,
            ...props.field.props,
            modelValue: props.field.props.modelValue.value,
          });
      } else {
        return () =>
          h(props.field.component, { ...attrs, ...props.field.props });
      }
    }
  },
});
</script>
