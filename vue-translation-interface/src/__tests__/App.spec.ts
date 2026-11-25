import { describe, it, expect } from "vitest"

import { mount } from "@vue/test-utils"
import App from "../App.vue"

describe("App", () => {
  it("renders the router view", () => {
    const wrapper = mount(App, {
      global: {
        stubs: { RouterView: { template: '<div data-test="view" />' } },
      },
    })
    expect(wrapper.find("[data-test=view]").exists()).toBe(true)
  })
})
