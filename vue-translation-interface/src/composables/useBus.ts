// https://shouts.dev/data-pass-between-components-using-eventbus-in-vue3
import mitt from "mitt"

type Events = {
  "insert-symbol": InsertSymbol
}

const emitter = mitt<Events>()

export function useBus() {
  return { bus: emitter }
}
