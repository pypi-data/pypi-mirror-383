/*
 * Configuration for Vue router
 */

import routes from "../routes.js";
import { createRouter, createWebHistory } from "@/vue-router";

export const routerOpts = {
  history: createWebHistory(),
  routes,
};

export default createRouter(routerOpts);
