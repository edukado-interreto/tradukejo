/******/ (function(modules) { // webpackBootstrap
/******/ 	// install a JSONP callback for chunk loading
/******/ 	function webpackJsonpCallback(data) {
/******/ 		var chunkIds = data[0];
/******/ 		var moreModules = data[1];
/******/ 		var executeModules = data[2];
/******/
/******/ 		// add "moreModules" to the modules object,
/******/ 		// then flag all "chunkIds" as loaded and fire callback
/******/ 		var moduleId, chunkId, i = 0, resolves = [];
/******/ 		for(;i < chunkIds.length; i++) {
/******/ 			chunkId = chunkIds[i];
/******/ 			if(Object.prototype.hasOwnProperty.call(installedChunks, chunkId) && installedChunks[chunkId]) {
/******/ 				resolves.push(installedChunks[chunkId][0]);
/******/ 			}
/******/ 			installedChunks[chunkId] = 0;
/******/ 		}
/******/ 		for(moduleId in moreModules) {
/******/ 			if(Object.prototype.hasOwnProperty.call(moreModules, moduleId)) {
/******/ 				modules[moduleId] = moreModules[moduleId];
/******/ 			}
/******/ 		}
/******/ 		if(parentJsonpFunction) parentJsonpFunction(data);
/******/
/******/ 		while(resolves.length) {
/******/ 			resolves.shift()();
/******/ 		}
/******/
/******/ 		// add entry modules from loaded chunk to deferred list
/******/ 		deferredModules.push.apply(deferredModules, executeModules || []);
/******/
/******/ 		// run deferred modules when all chunks ready
/******/ 		return checkDeferredModules();
/******/ 	};
/******/ 	function checkDeferredModules() {
/******/ 		var result;
/******/ 		for(var i = 0; i < deferredModules.length; i++) {
/******/ 			var deferredModule = deferredModules[i];
/******/ 			var fulfilled = true;
/******/ 			for(var j = 1; j < deferredModule.length; j++) {
/******/ 				var depId = deferredModule[j];
/******/ 				if(installedChunks[depId] !== 0) fulfilled = false;
/******/ 			}
/******/ 			if(fulfilled) {
/******/ 				deferredModules.splice(i--, 1);
/******/ 				result = __webpack_require__(__webpack_require__.s = deferredModule[0]);
/******/ 			}
/******/ 		}
/******/
/******/ 		return result;
/******/ 	}
/******/
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// object to store loaded and loading chunks
/******/ 	// undefined = chunk not loaded, null = chunk preloaded/prefetched
/******/ 	// Promise = chunk loading, 0 = chunk loaded
/******/ 	var installedChunks = {
/******/ 		"app": 0
/******/ 	};
/******/
/******/ 	var deferredModules = [];
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "/";
/******/
/******/ 	var jsonpArray = window["webpackJsonp"] = window["webpackJsonp"] || [];
/******/ 	var oldJsonpFunction = jsonpArray.push.bind(jsonpArray);
/******/ 	jsonpArray.push = webpackJsonpCallback;
/******/ 	jsonpArray = jsonpArray.slice();
/******/ 	for(var i = 0; i < jsonpArray.length; i++) webpackJsonpCallback(jsonpArray[i]);
/******/ 	var parentJsonpFunction = oldJsonpFunction;
/******/
/******/
/******/ 	// add entry module to deferred list
/******/ 	deferredModules.push([0,"chunk-vendors"]);
/******/ 	// run deferred modules when ready
/******/ 	return checkDeferredModules();
/******/ })
/************************************************************************/
/******/ ({

/***/ "./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/App.vue?vue&type=script&lang=js":
/*!*******************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1!./src/App.vue?vue&type=script&lang=js ***!
  \*******************************************************************************************************************************************************************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony default export */ __webpack_exports__[\"default\"] = ({\n  name: 'App',\n  components: {}\n});\n\n//# sourceURL=webpack:///./src/App.vue?./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1");

/***/ }),

/***/ "./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/components/FilterBar.vue?vue&type=script&lang=js":
/*!************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1!./src/components/FilterBar.vue?vue&type=script&lang=js ***!
  \************************************************************************************************************************************************************************************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony default export */ __webpack_exports__[\"default\"] = ({});\n\n//# sourceURL=webpack:///./src/components/FilterBar.vue?./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1");

/***/ }),

/***/ "./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/components/NavigationBar.vue?vue&type=script&lang=js":
/*!****************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1!./src/components/NavigationBar.vue?vue&type=script&lang=js ***!
  \****************************************************************************************************************************************************************************************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony default export */ __webpack_exports__[\"default\"] = ({\n  computed: {\n    currentLanguage: function currentLanguage() {\n      return this.$store.getters.currentLanguage;\n    }\n  }\n});\n\n//# sourceURL=webpack:///./src/components/NavigationBar.vue?./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1");

/***/ }),

/***/ "./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/components/TranslationZone.vue?vue&type=script&lang=js":
/*!******************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1!./src/components/TranslationZone.vue?vue&type=script&lang=js ***!
  \******************************************************************************************************************************************************************************************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _translation_TranslationRow__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./translation/TranslationRow */ \"./src/components/translation/TranslationRow.vue\");\n\n/* harmony default export */ __webpack_exports__[\"default\"] = ({\n  components: {\n    TranslationRow: _translation_TranslationRow__WEBPACK_IMPORTED_MODULE_0__[\"default\"]\n  },\n  props: ['strings']\n});\n\n//# sourceURL=webpack:///./src/components/TranslationZone.vue?./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1");

/***/ }),

/***/ "./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/components/translation/TranslationRow.vue?vue&type=script&lang=js":
/*!*****************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1!./src/components/translation/TranslationRow.vue?vue&type=script&lang=js ***!
  \*****************************************************************************************************************************************************************************************************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony default export */ __webpack_exports__[\"default\"] = ({\n  props: ['string'],\n  computed: {\n    translationRowClasses: function translationRowClasses() {\n      return {\n        translated: this.string.state === this.globals.TRANSLATION_STATE_TRANSLATED,\n        outdated: this.string.state === this.globals.TRANSLATION_STATE_OUTDATED,\n        untranslated: this.string.state === this.globals.TRANSLATION_STATE_UNTRANSLATED\n      };\n    }\n  }\n});\n\n//# sourceURL=webpack:///./src/components/translation/TranslationRow.vue?./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1");

/***/ }),

/***/ "./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/pages/TranslateLanguage.vue?vue&type=script&lang=js":
/*!***************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1!./src/pages/TranslateLanguage.vue?vue&type=script&lang=js ***!
  \***************************************************************************************************************************************************************************************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var core_js_modules_es_array_concat_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! core-js/modules/es.array.concat.js */ \"./node_modules/core-js/modules/es.array.concat.js\");\n/* harmony import */ var core_js_modules_es_array_concat_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_array_concat_js__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var regenerator_runtime_runtime_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! regenerator-runtime/runtime.js */ \"./node_modules/regenerator-runtime/runtime.js\");\n/* harmony import */ var regenerator_runtime_runtime_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(regenerator_runtime_runtime_js__WEBPACK_IMPORTED_MODULE_1__);\n/* harmony import */ var _home_matthieu_Sites_ikso_tradukejo_vue_translation_interface_node_modules_babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/asyncToGenerator */ \"./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js\");\n/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! axios */ \"./node_modules/axios/index.js\");\n/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(axios__WEBPACK_IMPORTED_MODULE_3__);\n/* harmony import */ var _components_FilterBar__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../components/FilterBar */ \"./src/components/FilterBar.vue\");\n/* harmony import */ var _components_NavigationBar__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../components/NavigationBar */ \"./src/components/NavigationBar.vue\");\n/* harmony import */ var _components_TranslationZone__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../components/TranslationZone */ \"./src/components/TranslationZone.vue\");\n\n\n\n\n\n\n\n/* harmony default export */ __webpack_exports__[\"default\"] = ({\n  components: {\n    FilterBar: _components_FilterBar__WEBPACK_IMPORTED_MODULE_4__[\"default\"],\n    NavigationBar: _components_NavigationBar__WEBPACK_IMPORTED_MODULE_5__[\"default\"],\n    TranslationZone: _components_TranslationZone__WEBPACK_IMPORTED_MODULE_6__[\"default\"]\n  },\n  data: function data() {\n    return {\n      currentDirectory: \"\",\n      searchString: \"\",\n      stateFilter: \"\",\n      sort: \"\",\n      trstrings: []\n    };\n  },\n  computed: {\n    paramLang: function paramLang() {\n      return this.$route.params.lang;\n    },\n    currentLanguage: function currentLanguage() {\n      return this.$store.getters.currentLanguage;\n    }\n  },\n  watch: {\n    paramLang: function paramLang(newValue) {\n      this.setLanguage(newValue);\n    }\n  },\n  methods: {\n    setLanguage: function setLanguage(code) {\n      this.$store.dispatch(\"setLanguage\", code);\n    },\n    fetchStrings: function fetchStrings() {\n      var _this = this;\n\n      return Object(_home_matthieu_Sites_ikso_tradukejo_vue_translation_interface_node_modules_babel_runtime_helpers_esm_asyncToGenerator__WEBPACK_IMPORTED_MODULE_2__[\"default\"])( /*#__PURE__*/regeneratorRuntime.mark(function _callee() {\n        return regeneratorRuntime.wrap(function _callee$(_context) {\n          while (1) {\n            switch (_context.prev = _context.next) {\n              case 0:\n                _context.next = 2;\n                return axios__WEBPACK_IMPORTED_MODULE_3___default.a.post(\"/vue/get-strings/\".concat(_this.projectId, \"/\").concat(_this.currentLanguage.pk, \"/\"), {\n                  dir: _this.currentDirectory,\n                  q: _this.searchString,\n                  state: _this.stateFilter,\n                  sort: _this.sort\n                }).then(function (response) {\n                  _this.trstrings = response.data.strings;\n                }).catch(function (error) {\n                  console.log(error);\n                });\n\n              case 2:\n              case \"end\":\n                return _context.stop();\n            }\n          }\n        }, _callee);\n      }))();\n    }\n  },\n  created: function created() {\n    this.setLanguage(this.paramLang);\n    this.fetchStrings();\n  }\n});\n\n//# sourceURL=webpack:///./src/pages/TranslateLanguage.vue?./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1");

/***/ }),

/***/ "./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader-v16/dist/templateLoader.js?!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/App.vue?vue&type=template&id=7ba5bd90":
/*!**************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1!./src/App.vue?vue&type=template&id=7ba5bd90 ***!
  \**************************************************************************************************************************************************************************************************************************************************************************************************/
/*! exports provided: render */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"render\", function() { return render; });\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"./node_modules/vue/dist/vue.runtime.esm-bundler.js\");\n\nfunction render(_ctx, _cache, $props, $setup, $data, $options) {\n  var _component_router_view = Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"resolveComponent\"])(\"router-view\");\n\n  return Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"openBlock\"])(), Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createBlock\"])(_component_router_view);\n}\n\n//# sourceURL=webpack:///./src/App.vue?./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1");

/***/ }),

/***/ "./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader-v16/dist/templateLoader.js?!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/components/FilterBar.vue?vue&type=template&id=d2b6b00a":
/*!*******************************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1!./src/components/FilterBar.vue?vue&type=template&id=d2b6b00a ***!
  \*******************************************************************************************************************************************************************************************************************************************************************************************************************/
/*! exports provided: render */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"render\", function() { return render; });\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"./node_modules/vue/dist/vue.runtime.esm-bundler.js\");\n\nvar _hoisted_1 = {\n  class: \"navbar navbar-expand-lg navbar-light bg-light\"\n};\n\nvar _hoisted_2 = /*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createVNode\"])(\"ul\", {\n  class: \"navbar-nav mr-auto\"\n}, [/*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createVNode\"])(\"li\", {\n  class: \"nav-item dropdown\"\n}, [/*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createVNode\"])(\"a\", {\n  class: \"nav-link dropdown-toggle\",\n  href: \"#\",\n  id: \"stringStateDropdown\",\n  role: \"button\",\n  \"data-toggle\": \"dropdown\",\n  \"aria-haspopup\": \"true\",\n  \"aria-expanded\": \"false\"\n}, \" Ĉiuj ĉenoj \"), /*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createVNode\"])(\"div\", {\n  class: \"dropdown-menu\",\n  \"aria-labelledby\": \"stringStateDropdown\"\n}, [/*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createVNode\"])(\"a\", {\n  class: \"dropdown-item\",\n  href: \"./\"\n}, \"Ĉiuj ĉenoj\"), /*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createVNode\"])(\"a\", {\n  class: \"dropdown-item\",\n  href: \"./?state=untr\"\n}, \"Nur netradukitaj\"), /*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createVNode\"])(\"a\", {\n  class: \"dropdown-item\",\n  href: \"./?state=outd\"\n}, \"Nur retradukendaj\"), /*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createVNode\"])(\"a\", {\n  class: \"dropdown-item\",\n  href: \"./?state=unout\"\n}, \"Netradukitaj kaj retradukendaj\")])]), /*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createVNode\"])(\"li\", {\n  class: \"nav-item dropdown\"\n}, [/*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createVNode\"])(\"a\", {\n  class: \"nav-link dropdown-toggle\",\n  href: \"#\",\n  id: \"sortDropdown\",\n  role: \"button\",\n  \"data-toggle\": \"dropdown\",\n  \"aria-haspopup\": \"true\",\n  \"aria-expanded\": \"false\"\n}, \" Ordigi laŭ nomo \"), /*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createVNode\"])(\"div\", {\n  class: \"dropdown-menu\",\n  \"aria-labelledby\": \"sortDropdown\"\n}, [/*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createVNode\"])(\"a\", {\n  class: \"dropdown-item\",\n  href: \"./\"\n}, \"Ordigi laŭ nomo\"), /*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createVNode\"])(\"a\", {\n  class: \"dropdown-item\",\n  href: \"./?sort=old\"\n}, \"Ordigi laŭ plej malnovaj\"), /*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createVNode\"])(\"a\", {\n  class: \"dropdown-item\",\n  href: \"./?sort=new\"\n}, \"Ordigi laŭ plej novaj\")])])], -1\n/* HOISTED */\n);\n\nvar _hoisted_3 = /*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createVNode\"])(\"form\", {\n  class: \"form-inline my-2 my-lg-0\",\n  action: \"/translate/7/eo/\",\n  method: \"get\"\n}, [/*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createVNode\"])(\"input\", {\n  class: \"form-control mr-sm-2\",\n  type: \"search\",\n  placeholder: \"Serĉi…\",\n  \"aria-label\": \"Serĉi\",\n  value: \"\",\n  name: \"q\"\n}), /*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createVNode\"])(\"button\", {\n  class: \"btn btn-secondary\",\n  type: \"submit\"\n}, \"Serĉi\")], -1\n/* HOISTED */\n);\n\nfunction render(_ctx, _cache, $props, $setup, $data, $options) {\n  return Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"openBlock\"])(), Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createBlock\"])(\"nav\", _hoisted_1, [_hoisted_2, _hoisted_3]);\n}\n\n//# sourceURL=webpack:///./src/components/FilterBar.vue?./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1");

/***/ }),

/***/ "./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader-v16/dist/templateLoader.js?!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/components/NavigationBar.vue?vue&type=template&id=d1a7e442":
/*!***********************************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1!./src/components/NavigationBar.vue?vue&type=template&id=d1a7e442 ***!
  \***********************************************************************************************************************************************************************************************************************************************************************************************************************/
/*! exports provided: render */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"render\", function() { return render; });\n/* harmony import */ var core_js_modules_es_function_name_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! core-js/modules/es.function.name.js */ \"./node_modules/core-js/modules/es.function.name.js\");\n/* harmony import */ var core_js_modules_es_function_name_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_function_name_js__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! vue */ \"./node_modules/vue/dist/vue.runtime.esm-bundler.js\");\n\n\nvar _hoisted_1 = {\n  \"aria-label\": \"breadcrumb\",\n  class: \"my-4\"\n};\nvar _hoisted_2 = {\n  class: \"breadcrumb translation-path p-1\"\n};\nvar _hoisted_3 = {\n  class: \"breadcrumb-item\"\n};\nvar _hoisted_4 = {\n  class: \"dropdown\"\n};\nvar _hoisted_5 = {\n  class: \"dropdown-toggle\",\n  href: \"#\",\n  type: \"button\",\n  id: \"dropdownLanguageVersionButton\",\n  \"data-toggle\": \"dropdown\",\n  \"aria-haspopup\": \"true\",\n  \"aria-expanded\": \"false\"\n};\nvar _hoisted_6 = {\n  class: \"dropdown-menu\",\n  \"aria-labelledby\": \"dropdownLanguageVersionButton\"\n};\n\nvar _hoisted_7 = /*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createVNode\"])(\"li\", {\n  class: \"breadcrumb-item\"\n}, [/*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createVNode\"])(\"a\", {\n  href: \"/translate/7/eo/\"\n}, [/*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createVNode\"])(\"i\", {\n  class: \"fas fa-home\"\n})])], -1\n/* HOISTED */\n);\n\nvar _hoisted_8 = /*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createVNode\"])(\"li\", {\n  class: \"breadcrumb-item\",\n  \"aria-current\": \"page\"\n}, \"contact\", -1\n/* HOISTED */\n);\n\nfunction render(_ctx, _cache, $props, $setup, $data, $options) {\n  var _component_router_link = Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"resolveComponent\"])(\"router-link\");\n\n  return Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"openBlock\"])(), Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createBlock\"])(\"nav\", _hoisted_1, [Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createVNode\"])(\"ol\", _hoisted_2, [Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createVNode\"])(\"li\", _hoisted_3, [Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createVNode\"])(\"span\", _hoisted_4, [Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createVNode\"])(\"a\", _hoisted_5, Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"toDisplayString\"])($options.currentLanguage.fields.name), 1\n  /* TEXT */\n  ), Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createVNode\"])(\"div\", _hoisted_6, [(Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"openBlock\"])(true), Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createBlock\"])(vue__WEBPACK_IMPORTED_MODULE_1__[\"Fragment\"], null, Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"renderList\"])(_ctx.availableLanguages, function (language) {\n    return Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"openBlock\"])(), Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createBlock\"])(_component_router_link, {\n      key: language,\n      to: {\n        name: 'translateLanguage',\n        params: {\n          lang: language.pk\n        }\n      },\n      class: \"dropdown-item\"\n    }, {\n      default: Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"withCtx\"])(function () {\n        return [Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createTextVNode\"])(Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"toDisplayString\"])(language.fields.name), 1\n        /* TEXT */\n        )];\n      }),\n      _: 2\n      /* DYNAMIC */\n\n    }, 1032\n    /* PROPS, DYNAMIC_SLOTS */\n    , [\"to\"]);\n  }), 128\n  /* KEYED_FRAGMENT */\n  ))])])]), _hoisted_7, _hoisted_8])]);\n}\n\n//# sourceURL=webpack:///./src/components/NavigationBar.vue?./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1");

/***/ }),

/***/ "./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader-v16/dist/templateLoader.js?!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/components/TranslationZone.vue?vue&type=template&id=caa46506":
/*!*************************************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1!./src/components/TranslationZone.vue?vue&type=template&id=caa46506 ***!
  \*************************************************************************************************************************************************************************************************************************************************************************************************************************/
/*! exports provided: render */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"render\", function() { return render; });\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"./node_modules/vue/dist/vue.runtime.esm-bundler.js\");\n\nfunction render(_ctx, _cache, $props, $setup, $data, $options) {\n  var _component_translation_row = Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"resolveComponent\"])(\"translation-row\");\n\n  return Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"openBlock\"])(true), Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createBlock\"])(vue__WEBPACK_IMPORTED_MODULE_0__[\"Fragment\"], null, Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"renderList\"])($props.strings, function (string) {\n    return Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"openBlock\"])(), Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createBlock\"])(_component_translation_row, {\n      key: string.id,\n      string: string\n    }, null, 8\n    /* PROPS */\n    , [\"string\"]);\n  }), 128\n  /* KEYED_FRAGMENT */\n  );\n}\n\n//# sourceURL=webpack:///./src/components/TranslationZone.vue?./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1");

/***/ }),

/***/ "./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader-v16/dist/templateLoader.js?!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/components/translation/TranslationRow.vue?vue&type=template&id=112bbb37":
/*!************************************************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1!./src/components/translation/TranslationRow.vue?vue&type=template&id=112bbb37 ***!
  \************************************************************************************************************************************************************************************************************************************************************************************************************************************/
/*! exports provided: render */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"render\", function() { return render; });\n/* harmony import */ var core_js_modules_es_function_name_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! core-js/modules/es.function.name.js */ \"./node_modules/core-js/modules/es.function.name.js\");\n/* harmony import */ var core_js_modules_es_function_name_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_function_name_js__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! vue */ \"./node_modules/vue/dist/vue.runtime.esm-bundler.js\");\n\n\nvar _hoisted_1 = {\n  class: \"row\"\n};\nvar _hoisted_2 = {\n  class: \"col-6\"\n};\nvar _hoisted_3 = {\n  title: \"Titolo de la ĉeno, ne traduku ĝin\"\n};\n\nvar _hoisted_4 = /*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createTextVNode\"])(\" – \");\n\nvar _hoisted_5 = /*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createVNode\"])(\"div\", {\n  class: \"col-6 text-right translation-state-bar\"\n}, null, -1\n/* HOISTED */\n);\n\nvar _hoisted_6 = {\n  class: \"row mt-1{% if str.state == TRANSLATION_STATE_UNTRANSLATED %} d-flex align-items-center{% endif %}\"\n};\nvar _hoisted_7 = {\n  class: \"col-md-6 original-string\"\n};\nvar _hoisted_8 = {\n  class: \"col-md-6 translation-widget\"\n};\nfunction render(_ctx, _cache, $props, $setup, $data, $options) {\n  return Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"openBlock\"])(), Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createBlock\"])(\"div\", {\n    class: [\"translation-row\", $options.translationRowClasses]\n  }, [Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createVNode\"])(\"div\", _hoisted_1, [Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createVNode\"])(\"div\", _hoisted_2, [Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createVNode\"])(\"strong\", _hoisted_3, \"#\" + Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"toDisplayString\"])($props.string.name), 1\n  /* TEXT */\n  ), _hoisted_4]), _hoisted_5]), Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createVNode\"])(\"div\", _hoisted_6, [Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createVNode\"])(\"div\", _hoisted_7, Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"toDisplayString\"])($props.string.original_text.text), 1\n  /* TEXT */\n  ), Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createVNode\"])(\"div\", _hoisted_8, Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"toDisplayString\"])($props.string.translated_text.text), 1\n  /* TEXT */\n  )])], 2\n  /* CLASS */\n  );\n}\n\n//# sourceURL=webpack:///./src/components/translation/TranslationRow.vue?./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1");

/***/ }),

/***/ "./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader-v16/dist/templateLoader.js?!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/pages/LanguageChoice.vue?vue&type=template&id=7706a63d":
/*!*******************************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1!./src/pages/LanguageChoice.vue?vue&type=template&id=7706a63d ***!
  \*******************************************************************************************************************************************************************************************************************************************************************************************************************/
/*! exports provided: render */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"render\", function() { return render; });\n/* harmony import */ var core_js_modules_es_function_name_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! core-js/modules/es.function.name.js */ \"./node_modules/core-js/modules/es.function.name.js\");\n/* harmony import */ var core_js_modules_es_function_name_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_function_name_js__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! vue */ \"./node_modules/vue/dist/vue.runtime.esm-bundler.js\");\n\n\n\nvar _hoisted_1 = /*#__PURE__*/Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createVNode\"])(\"h3\", null, \"Elektu la lingvon, al kiu vi volas traduki\", -1\n/* HOISTED */\n);\n\nvar _hoisted_2 = {\n  class: \"row\"\n};\nfunction render(_ctx, _cache) {\n  var _component_router_link = Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"resolveComponent\"])(\"router-link\");\n\n  return Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"openBlock\"])(), Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createBlock\"])(vue__WEBPACK_IMPORTED_MODULE_1__[\"Fragment\"], null, [_hoisted_1, Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createVNode\"])(\"div\", _hoisted_2, [(Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"openBlock\"])(true), Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createBlock\"])(vue__WEBPACK_IMPORTED_MODULE_1__[\"Fragment\"], null, Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"renderList\"])(_ctx.availableLanguages, function (language) {\n    return Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"openBlock\"])(), Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createBlock\"])(\"div\", {\n      class: \"col-6 col-sm-4 col-md-3 col-lx-2 vue-language-selector\",\n      key: language.pk,\n      lang: language.pk,\n      dir: language.fields.direction\n    }, [Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createVNode\"])(_component_router_link, {\n      to: {\n        name: 'translateLanguage',\n        params: {\n          lang: language.pk\n        }\n      }\n    }, {\n      default: Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"withCtx\"])(function () {\n        return [Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"createTextVNode\"])(Object(vue__WEBPACK_IMPORTED_MODULE_1__[\"toDisplayString\"])(language.fields.name), 1\n        /* TEXT */\n        )];\n      }),\n      _: 2\n      /* DYNAMIC */\n\n    }, 1032\n    /* PROPS, DYNAMIC_SLOTS */\n    , [\"to\"])], 8\n    /* PROPS */\n    , [\"lang\", \"dir\"]);\n  }), 128\n  /* KEYED_FRAGMENT */\n  ))])], 64\n  /* STABLE_FRAGMENT */\n  );\n}\n\n//# sourceURL=webpack:///./src/pages/LanguageChoice.vue?./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1");

/***/ }),

/***/ "./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader-v16/dist/templateLoader.js?!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/pages/TranslateLanguage.vue?vue&type=template&id=6c6a7c5c":
/*!**********************************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1!./src/pages/TranslateLanguage.vue?vue&type=template&id=6c6a7c5c ***!
  \**********************************************************************************************************************************************************************************************************************************************************************************************************************/
/*! exports provided: render */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"render\", function() { return render; });\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"./node_modules/vue/dist/vue.runtime.esm-bundler.js\");\n\nfunction render(_ctx, _cache, $props, $setup, $data, $options) {\n  var _component_filter_bar = Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"resolveComponent\"])(\"filter-bar\");\n\n  var _component_navigation_bar = Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"resolveComponent\"])(\"navigation-bar\");\n\n  var _component_translation_zone = Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"resolveComponent\"])(\"translation-zone\");\n\n  return Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"openBlock\"])(), Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createBlock\"])(vue__WEBPACK_IMPORTED_MODULE_0__[\"Fragment\"], null, [Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createVNode\"])(_component_filter_bar), Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createVNode\"])(_component_navigation_bar), Object(vue__WEBPACK_IMPORTED_MODULE_0__[\"createVNode\"])(_component_translation_zone, {\n    strings: $data.trstrings\n  }, null, 8\n  /* PROPS */\n  , [\"strings\"])], 64\n  /* STABLE_FRAGMENT */\n  );\n}\n\n//# sourceURL=webpack:///./src/pages/TranslateLanguage.vue?./node_modules/cache-loader/dist/cjs.js??ref--12-0!./node_modules/babel-loader/lib!./node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!./node_modules/cache-loader/dist/cjs.js??ref--0-0!./node_modules/vue-loader-v16/dist??ref--0-1");

/***/ }),

/***/ "./src/App.vue":
/*!*********************!*\
  !*** ./src/App.vue ***!
  \*********************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _App_vue_vue_type_template_id_7ba5bd90__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./App.vue?vue&type=template&id=7ba5bd90 */ \"./src/App.vue?vue&type=template&id=7ba5bd90\");\n/* harmony import */ var _App_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./App.vue?vue&type=script&lang=js */ \"./src/App.vue?vue&type=script&lang=js\");\n/* empty/unused harmony star reexport */\n\n\n_App_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"].render = _App_vue_vue_type_template_id_7ba5bd90__WEBPACK_IMPORTED_MODULE_0__[\"render\"]\n/* hot reload */\nif (false) {}\n\n_App_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"].__file = \"src/App.vue\"\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (_App_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"]);\n\n//# sourceURL=webpack:///./src/App.vue?");

/***/ }),

/***/ "./src/App.vue?vue&type=script&lang=js":
/*!*********************************************!*\
  !*** ./src/App.vue?vue&type=script&lang=js ***!
  \*********************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_App_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../node_modules/cache-loader/dist/cjs.js??ref--12-0!../node_modules/babel-loader/lib!../node_modules/cache-loader/dist/cjs.js??ref--0-0!../node_modules/vue-loader-v16/dist??ref--0-1!./App.vue?vue&type=script&lang=js */ \"./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/App.vue?vue&type=script&lang=js\");\n/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, \"default\", function() { return _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_App_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__[\"default\"]; });\n\n/* empty/unused harmony star reexport */ \n\n//# sourceURL=webpack:///./src/App.vue?");

/***/ }),

/***/ "./src/App.vue?vue&type=template&id=7ba5bd90":
/*!***************************************************!*\
  !*** ./src/App.vue?vue&type=template&id=7ba5bd90 ***!
  \***************************************************/
/*! exports provided: render */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_vue_loader_v16_dist_templateLoader_js_ref_6_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_App_vue_vue_type_template_id_7ba5bd90__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../node_modules/cache-loader/dist/cjs.js??ref--12-0!../node_modules/babel-loader/lib!../node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!../node_modules/cache-loader/dist/cjs.js??ref--0-0!../node_modules/vue-loader-v16/dist??ref--0-1!./App.vue?vue&type=template&id=7ba5bd90 */ \"./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader-v16/dist/templateLoader.js?!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/App.vue?vue&type=template&id=7ba5bd90\");\n/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, \"render\", function() { return _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_vue_loader_v16_dist_templateLoader_js_ref_6_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_App_vue_vue_type_template_id_7ba5bd90__WEBPACK_IMPORTED_MODULE_0__[\"render\"]; });\n\n\n\n//# sourceURL=webpack:///./src/App.vue?");

/***/ }),

/***/ "./src/components/FilterBar.vue":
/*!**************************************!*\
  !*** ./src/components/FilterBar.vue ***!
  \**************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _FilterBar_vue_vue_type_template_id_d2b6b00a__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./FilterBar.vue?vue&type=template&id=d2b6b00a */ \"./src/components/FilterBar.vue?vue&type=template&id=d2b6b00a\");\n/* harmony import */ var _FilterBar_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./FilterBar.vue?vue&type=script&lang=js */ \"./src/components/FilterBar.vue?vue&type=script&lang=js\");\n/* empty/unused harmony star reexport */\n\n\n_FilterBar_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"].render = _FilterBar_vue_vue_type_template_id_d2b6b00a__WEBPACK_IMPORTED_MODULE_0__[\"render\"]\n/* hot reload */\nif (false) {}\n\n_FilterBar_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"].__file = \"src/components/FilterBar.vue\"\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (_FilterBar_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"]);\n\n//# sourceURL=webpack:///./src/components/FilterBar.vue?");

/***/ }),

/***/ "./src/components/FilterBar.vue?vue&type=script&lang=js":
/*!**************************************************************!*\
  !*** ./src/components/FilterBar.vue?vue&type=script&lang=js ***!
  \**************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_FilterBar_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/cache-loader/dist/cjs.js??ref--12-0!../../node_modules/babel-loader/lib!../../node_modules/cache-loader/dist/cjs.js??ref--0-0!../../node_modules/vue-loader-v16/dist??ref--0-1!./FilterBar.vue?vue&type=script&lang=js */ \"./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/components/FilterBar.vue?vue&type=script&lang=js\");\n/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, \"default\", function() { return _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_FilterBar_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__[\"default\"]; });\n\n/* empty/unused harmony star reexport */ \n\n//# sourceURL=webpack:///./src/components/FilterBar.vue?");

/***/ }),

/***/ "./src/components/FilterBar.vue?vue&type=template&id=d2b6b00a":
/*!********************************************************************!*\
  !*** ./src/components/FilterBar.vue?vue&type=template&id=d2b6b00a ***!
  \********************************************************************/
/*! exports provided: render */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_vue_loader_v16_dist_templateLoader_js_ref_6_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_FilterBar_vue_vue_type_template_id_d2b6b00a__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/cache-loader/dist/cjs.js??ref--12-0!../../node_modules/babel-loader/lib!../../node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!../../node_modules/cache-loader/dist/cjs.js??ref--0-0!../../node_modules/vue-loader-v16/dist??ref--0-1!./FilterBar.vue?vue&type=template&id=d2b6b00a */ \"./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader-v16/dist/templateLoader.js?!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/components/FilterBar.vue?vue&type=template&id=d2b6b00a\");\n/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, \"render\", function() { return _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_vue_loader_v16_dist_templateLoader_js_ref_6_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_FilterBar_vue_vue_type_template_id_d2b6b00a__WEBPACK_IMPORTED_MODULE_0__[\"render\"]; });\n\n\n\n//# sourceURL=webpack:///./src/components/FilterBar.vue?");

/***/ }),

/***/ "./src/components/NavigationBar.vue":
/*!******************************************!*\
  !*** ./src/components/NavigationBar.vue ***!
  \******************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _NavigationBar_vue_vue_type_template_id_d1a7e442__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./NavigationBar.vue?vue&type=template&id=d1a7e442 */ \"./src/components/NavigationBar.vue?vue&type=template&id=d1a7e442\");\n/* harmony import */ var _NavigationBar_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./NavigationBar.vue?vue&type=script&lang=js */ \"./src/components/NavigationBar.vue?vue&type=script&lang=js\");\n/* empty/unused harmony star reexport */\n\n\n_NavigationBar_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"].render = _NavigationBar_vue_vue_type_template_id_d1a7e442__WEBPACK_IMPORTED_MODULE_0__[\"render\"]\n/* hot reload */\nif (false) {}\n\n_NavigationBar_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"].__file = \"src/components/NavigationBar.vue\"\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (_NavigationBar_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"]);\n\n//# sourceURL=webpack:///./src/components/NavigationBar.vue?");

/***/ }),

/***/ "./src/components/NavigationBar.vue?vue&type=script&lang=js":
/*!******************************************************************!*\
  !*** ./src/components/NavigationBar.vue?vue&type=script&lang=js ***!
  \******************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_NavigationBar_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/cache-loader/dist/cjs.js??ref--12-0!../../node_modules/babel-loader/lib!../../node_modules/cache-loader/dist/cjs.js??ref--0-0!../../node_modules/vue-loader-v16/dist??ref--0-1!./NavigationBar.vue?vue&type=script&lang=js */ \"./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/components/NavigationBar.vue?vue&type=script&lang=js\");\n/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, \"default\", function() { return _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_NavigationBar_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__[\"default\"]; });\n\n/* empty/unused harmony star reexport */ \n\n//# sourceURL=webpack:///./src/components/NavigationBar.vue?");

/***/ }),

/***/ "./src/components/NavigationBar.vue?vue&type=template&id=d1a7e442":
/*!************************************************************************!*\
  !*** ./src/components/NavigationBar.vue?vue&type=template&id=d1a7e442 ***!
  \************************************************************************/
/*! exports provided: render */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_vue_loader_v16_dist_templateLoader_js_ref_6_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_NavigationBar_vue_vue_type_template_id_d1a7e442__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/cache-loader/dist/cjs.js??ref--12-0!../../node_modules/babel-loader/lib!../../node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!../../node_modules/cache-loader/dist/cjs.js??ref--0-0!../../node_modules/vue-loader-v16/dist??ref--0-1!./NavigationBar.vue?vue&type=template&id=d1a7e442 */ \"./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader-v16/dist/templateLoader.js?!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/components/NavigationBar.vue?vue&type=template&id=d1a7e442\");\n/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, \"render\", function() { return _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_vue_loader_v16_dist_templateLoader_js_ref_6_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_NavigationBar_vue_vue_type_template_id_d1a7e442__WEBPACK_IMPORTED_MODULE_0__[\"render\"]; });\n\n\n\n//# sourceURL=webpack:///./src/components/NavigationBar.vue?");

/***/ }),

/***/ "./src/components/TranslationZone.vue":
/*!********************************************!*\
  !*** ./src/components/TranslationZone.vue ***!
  \********************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _TranslationZone_vue_vue_type_template_id_caa46506__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./TranslationZone.vue?vue&type=template&id=caa46506 */ \"./src/components/TranslationZone.vue?vue&type=template&id=caa46506\");\n/* harmony import */ var _TranslationZone_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./TranslationZone.vue?vue&type=script&lang=js */ \"./src/components/TranslationZone.vue?vue&type=script&lang=js\");\n/* empty/unused harmony star reexport */\n\n\n_TranslationZone_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"].render = _TranslationZone_vue_vue_type_template_id_caa46506__WEBPACK_IMPORTED_MODULE_0__[\"render\"]\n/* hot reload */\nif (false) {}\n\n_TranslationZone_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"].__file = \"src/components/TranslationZone.vue\"\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (_TranslationZone_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"]);\n\n//# sourceURL=webpack:///./src/components/TranslationZone.vue?");

/***/ }),

/***/ "./src/components/TranslationZone.vue?vue&type=script&lang=js":
/*!********************************************************************!*\
  !*** ./src/components/TranslationZone.vue?vue&type=script&lang=js ***!
  \********************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_TranslationZone_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/cache-loader/dist/cjs.js??ref--12-0!../../node_modules/babel-loader/lib!../../node_modules/cache-loader/dist/cjs.js??ref--0-0!../../node_modules/vue-loader-v16/dist??ref--0-1!./TranslationZone.vue?vue&type=script&lang=js */ \"./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/components/TranslationZone.vue?vue&type=script&lang=js\");\n/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, \"default\", function() { return _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_TranslationZone_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__[\"default\"]; });\n\n/* empty/unused harmony star reexport */ \n\n//# sourceURL=webpack:///./src/components/TranslationZone.vue?");

/***/ }),

/***/ "./src/components/TranslationZone.vue?vue&type=template&id=caa46506":
/*!**************************************************************************!*\
  !*** ./src/components/TranslationZone.vue?vue&type=template&id=caa46506 ***!
  \**************************************************************************/
/*! exports provided: render */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_vue_loader_v16_dist_templateLoader_js_ref_6_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_TranslationZone_vue_vue_type_template_id_caa46506__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/cache-loader/dist/cjs.js??ref--12-0!../../node_modules/babel-loader/lib!../../node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!../../node_modules/cache-loader/dist/cjs.js??ref--0-0!../../node_modules/vue-loader-v16/dist??ref--0-1!./TranslationZone.vue?vue&type=template&id=caa46506 */ \"./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader-v16/dist/templateLoader.js?!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/components/TranslationZone.vue?vue&type=template&id=caa46506\");\n/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, \"render\", function() { return _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_vue_loader_v16_dist_templateLoader_js_ref_6_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_TranslationZone_vue_vue_type_template_id_caa46506__WEBPACK_IMPORTED_MODULE_0__[\"render\"]; });\n\n\n\n//# sourceURL=webpack:///./src/components/TranslationZone.vue?");

/***/ }),

/***/ "./src/components/translation/TranslationRow.vue":
/*!*******************************************************!*\
  !*** ./src/components/translation/TranslationRow.vue ***!
  \*******************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _TranslationRow_vue_vue_type_template_id_112bbb37__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./TranslationRow.vue?vue&type=template&id=112bbb37 */ \"./src/components/translation/TranslationRow.vue?vue&type=template&id=112bbb37\");\n/* harmony import */ var _TranslationRow_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./TranslationRow.vue?vue&type=script&lang=js */ \"./src/components/translation/TranslationRow.vue?vue&type=script&lang=js\");\n/* empty/unused harmony star reexport */\n\n\n_TranslationRow_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"].render = _TranslationRow_vue_vue_type_template_id_112bbb37__WEBPACK_IMPORTED_MODULE_0__[\"render\"]\n/* hot reload */\nif (false) {}\n\n_TranslationRow_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"].__file = \"src/components/translation/TranslationRow.vue\"\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (_TranslationRow_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"]);\n\n//# sourceURL=webpack:///./src/components/translation/TranslationRow.vue?");

/***/ }),

/***/ "./src/components/translation/TranslationRow.vue?vue&type=script&lang=js":
/*!*******************************************************************************!*\
  !*** ./src/components/translation/TranslationRow.vue?vue&type=script&lang=js ***!
  \*******************************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_TranslationRow_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/cache-loader/dist/cjs.js??ref--12-0!../../../node_modules/babel-loader/lib!../../../node_modules/cache-loader/dist/cjs.js??ref--0-0!../../../node_modules/vue-loader-v16/dist??ref--0-1!./TranslationRow.vue?vue&type=script&lang=js */ \"./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/components/translation/TranslationRow.vue?vue&type=script&lang=js\");\n/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, \"default\", function() { return _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_TranslationRow_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__[\"default\"]; });\n\n/* empty/unused harmony star reexport */ \n\n//# sourceURL=webpack:///./src/components/translation/TranslationRow.vue?");

/***/ }),

/***/ "./src/components/translation/TranslationRow.vue?vue&type=template&id=112bbb37":
/*!*************************************************************************************!*\
  !*** ./src/components/translation/TranslationRow.vue?vue&type=template&id=112bbb37 ***!
  \*************************************************************************************/
/*! exports provided: render */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_vue_loader_v16_dist_templateLoader_js_ref_6_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_TranslationRow_vue_vue_type_template_id_112bbb37__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../../node_modules/cache-loader/dist/cjs.js??ref--12-0!../../../node_modules/babel-loader/lib!../../../node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!../../../node_modules/cache-loader/dist/cjs.js??ref--0-0!../../../node_modules/vue-loader-v16/dist??ref--0-1!./TranslationRow.vue?vue&type=template&id=112bbb37 */ \"./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader-v16/dist/templateLoader.js?!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/components/translation/TranslationRow.vue?vue&type=template&id=112bbb37\");\n/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, \"render\", function() { return _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_vue_loader_v16_dist_templateLoader_js_ref_6_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_TranslationRow_vue_vue_type_template_id_112bbb37__WEBPACK_IMPORTED_MODULE_0__[\"render\"]; });\n\n\n\n//# sourceURL=webpack:///./src/components/translation/TranslationRow.vue?");

/***/ }),

/***/ "./src/main.js":
/*!*********************!*\
  !*** ./src/main.js ***!
  \*********************/
/*! no exports provided */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _home_matthieu_Sites_ikso_tradukejo_vue_translation_interface_node_modules_core_js_modules_es_array_iterator_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/core-js/modules/es.array.iterator.js */ \"./node_modules/core-js/modules/es.array.iterator.js\");\n/* harmony import */ var _home_matthieu_Sites_ikso_tradukejo_vue_translation_interface_node_modules_core_js_modules_es_array_iterator_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_home_matthieu_Sites_ikso_tradukejo_vue_translation_interface_node_modules_core_js_modules_es_array_iterator_js__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var _home_matthieu_Sites_ikso_tradukejo_vue_translation_interface_node_modules_core_js_modules_es_promise_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./node_modules/core-js/modules/es.promise.js */ \"./node_modules/core-js/modules/es.promise.js\");\n/* harmony import */ var _home_matthieu_Sites_ikso_tradukejo_vue_translation_interface_node_modules_core_js_modules_es_promise_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_home_matthieu_Sites_ikso_tradukejo_vue_translation_interface_node_modules_core_js_modules_es_promise_js__WEBPACK_IMPORTED_MODULE_1__);\n/* harmony import */ var _home_matthieu_Sites_ikso_tradukejo_vue_translation_interface_node_modules_core_js_modules_es_object_assign_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./node_modules/core-js/modules/es.object.assign.js */ \"./node_modules/core-js/modules/es.object.assign.js\");\n/* harmony import */ var _home_matthieu_Sites_ikso_tradukejo_vue_translation_interface_node_modules_core_js_modules_es_object_assign_js__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_home_matthieu_Sites_ikso_tradukejo_vue_translation_interface_node_modules_core_js_modules_es_object_assign_js__WEBPACK_IMPORTED_MODULE_2__);\n/* harmony import */ var _home_matthieu_Sites_ikso_tradukejo_vue_translation_interface_node_modules_core_js_modules_es_promise_finally_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./node_modules/core-js/modules/es.promise.finally.js */ \"./node_modules/core-js/modules/es.promise.finally.js\");\n/* harmony import */ var _home_matthieu_Sites_ikso_tradukejo_vue_translation_interface_node_modules_core_js_modules_es_promise_finally_js__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_home_matthieu_Sites_ikso_tradukejo_vue_translation_interface_node_modules_core_js_modules_es_promise_finally_js__WEBPACK_IMPORTED_MODULE_3__);\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! vue */ \"./node_modules/vue/dist/vue.runtime.esm-bundler.js\");\n/* harmony import */ var _App_vue__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./App.vue */ \"./src/App.vue\");\n/* harmony import */ var _router_js__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./router.js */ \"./src/router.js\");\n/* harmony import */ var _store_index_js__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./store/index.js */ \"./src/store/index.js\");\n\n\n\n\n\n\n\n\nvar app = Object(vue__WEBPACK_IMPORTED_MODULE_4__[\"createApp\"])(_App_vue__WEBPACK_IMPORTED_MODULE_5__[\"default\"]);\napp.use(_router_js__WEBPACK_IMPORTED_MODULE_6__[\"default\"]);\napp.use(_store_index_js__WEBPACK_IMPORTED_MODULE_7__[\"default\"]);\napp.config.globalProperties.availableLanguages = window.vueTranslationInterface.availableLanguages;\napp.config.globalProperties.projectId = window.vueTranslationInterface.projectId;\napp.config.globalProperties.globals = window.vueTranslationInterface.globals;\napp.mount('#app');\n\n//# sourceURL=webpack:///./src/main.js?");

/***/ }),

/***/ "./src/pages/LanguageChoice.vue":
/*!**************************************!*\
  !*** ./src/pages/LanguageChoice.vue ***!
  \**************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _LanguageChoice_vue_vue_type_template_id_7706a63d__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./LanguageChoice.vue?vue&type=template&id=7706a63d */ \"./src/pages/LanguageChoice.vue?vue&type=template&id=7706a63d\");\n\nconst script = {}\nscript.render = _LanguageChoice_vue_vue_type_template_id_7706a63d__WEBPACK_IMPORTED_MODULE_0__[\"render\"]\n/* hot reload */\nif (false) {}\n\nscript.__file = \"src/pages/LanguageChoice.vue\"\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (script);\n\n//# sourceURL=webpack:///./src/pages/LanguageChoice.vue?");

/***/ }),

/***/ "./src/pages/LanguageChoice.vue?vue&type=template&id=7706a63d":
/*!********************************************************************!*\
  !*** ./src/pages/LanguageChoice.vue?vue&type=template&id=7706a63d ***!
  \********************************************************************/
/*! exports provided: render */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_vue_loader_v16_dist_templateLoader_js_ref_6_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_LanguageChoice_vue_vue_type_template_id_7706a63d__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/cache-loader/dist/cjs.js??ref--12-0!../../node_modules/babel-loader/lib!../../node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!../../node_modules/cache-loader/dist/cjs.js??ref--0-0!../../node_modules/vue-loader-v16/dist??ref--0-1!./LanguageChoice.vue?vue&type=template&id=7706a63d */ \"./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader-v16/dist/templateLoader.js?!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/pages/LanguageChoice.vue?vue&type=template&id=7706a63d\");\n/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, \"render\", function() { return _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_vue_loader_v16_dist_templateLoader_js_ref_6_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_LanguageChoice_vue_vue_type_template_id_7706a63d__WEBPACK_IMPORTED_MODULE_0__[\"render\"]; });\n\n\n\n//# sourceURL=webpack:///./src/pages/LanguageChoice.vue?");

/***/ }),

/***/ "./src/pages/TranslateLanguage.vue":
/*!*****************************************!*\
  !*** ./src/pages/TranslateLanguage.vue ***!
  \*****************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _TranslateLanguage_vue_vue_type_template_id_6c6a7c5c__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./TranslateLanguage.vue?vue&type=template&id=6c6a7c5c */ \"./src/pages/TranslateLanguage.vue?vue&type=template&id=6c6a7c5c\");\n/* harmony import */ var _TranslateLanguage_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./TranslateLanguage.vue?vue&type=script&lang=js */ \"./src/pages/TranslateLanguage.vue?vue&type=script&lang=js\");\n/* empty/unused harmony star reexport */\n\n\n_TranslateLanguage_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"].render = _TranslateLanguage_vue_vue_type_template_id_6c6a7c5c__WEBPACK_IMPORTED_MODULE_0__[\"render\"]\n/* hot reload */\nif (false) {}\n\n_TranslateLanguage_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"].__file = \"src/pages/TranslateLanguage.vue\"\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (_TranslateLanguage_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"]);\n\n//# sourceURL=webpack:///./src/pages/TranslateLanguage.vue?");

/***/ }),

/***/ "./src/pages/TranslateLanguage.vue?vue&type=script&lang=js":
/*!*****************************************************************!*\
  !*** ./src/pages/TranslateLanguage.vue?vue&type=script&lang=js ***!
  \*****************************************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_TranslateLanguage_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/cache-loader/dist/cjs.js??ref--12-0!../../node_modules/babel-loader/lib!../../node_modules/cache-loader/dist/cjs.js??ref--0-0!../../node_modules/vue-loader-v16/dist??ref--0-1!./TranslateLanguage.vue?vue&type=script&lang=js */ \"./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/pages/TranslateLanguage.vue?vue&type=script&lang=js\");\n/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, \"default\", function() { return _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_TranslateLanguage_vue_vue_type_script_lang_js__WEBPACK_IMPORTED_MODULE_0__[\"default\"]; });\n\n/* empty/unused harmony star reexport */ \n\n//# sourceURL=webpack:///./src/pages/TranslateLanguage.vue?");

/***/ }),

/***/ "./src/pages/TranslateLanguage.vue?vue&type=template&id=6c6a7c5c":
/*!***********************************************************************!*\
  !*** ./src/pages/TranslateLanguage.vue?vue&type=template&id=6c6a7c5c ***!
  \***********************************************************************/
/*! exports provided: render */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_vue_loader_v16_dist_templateLoader_js_ref_6_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_TranslateLanguage_vue_vue_type_template_id_6c6a7c5c__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! -!../../node_modules/cache-loader/dist/cjs.js??ref--12-0!../../node_modules/babel-loader/lib!../../node_modules/vue-loader-v16/dist/templateLoader.js??ref--6!../../node_modules/cache-loader/dist/cjs.js??ref--0-0!../../node_modules/vue-loader-v16/dist??ref--0-1!./TranslateLanguage.vue?vue&type=template&id=6c6a7c5c */ \"./node_modules/cache-loader/dist/cjs.js?!./node_modules/babel-loader/lib/index.js!./node_modules/vue-loader-v16/dist/templateLoader.js?!./node_modules/cache-loader/dist/cjs.js?!./node_modules/vue-loader-v16/dist/index.js?!./src/pages/TranslateLanguage.vue?vue&type=template&id=6c6a7c5c\");\n/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, \"render\", function() { return _node_modules_cache_loader_dist_cjs_js_ref_12_0_node_modules_babel_loader_lib_index_js_node_modules_vue_loader_v16_dist_templateLoader_js_ref_6_node_modules_cache_loader_dist_cjs_js_ref_0_0_node_modules_vue_loader_v16_dist_index_js_ref_0_1_TranslateLanguage_vue_vue_type_template_id_6c6a7c5c__WEBPACK_IMPORTED_MODULE_0__[\"render\"]; });\n\n\n\n//# sourceURL=webpack:///./src/pages/TranslateLanguage.vue?");

/***/ }),

/***/ "./src/router.js":
/*!***********************!*\
  !*** ./src/router.js ***!
  \***********************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var vue_router__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue-router */ \"./node_modules/vue-router/dist/vue-router.esm-bundler.js\");\n/* harmony import */ var _pages_LanguageChoice__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./pages/LanguageChoice */ \"./src/pages/LanguageChoice.vue\");\n/* harmony import */ var _pages_TranslateLanguage__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./pages/TranslateLanguage */ \"./src/pages/TranslateLanguage.vue\");\n\n\n\nvar baseURL = window.vueTranslationInterface.baseURL;\nvar routes = [{\n  path: baseURL,\n  name: \"languageChoice\",\n  component: _pages_LanguageChoice__WEBPACK_IMPORTED_MODULE_1__[\"default\"]\n}, {\n  path: baseURL + \":lang\",\n  name: \"translateLanguage\",\n  component: _pages_TranslateLanguage__WEBPACK_IMPORTED_MODULE_2__[\"default\"]\n}];\nvar router = Object(vue_router__WEBPACK_IMPORTED_MODULE_0__[\"createRouter\"])({\n  history: Object(vue_router__WEBPACK_IMPORTED_MODULE_0__[\"createWebHistory\"])(),\n  routes: routes\n});\n/* harmony default export */ __webpack_exports__[\"default\"] = (router);\n\n//# sourceURL=webpack:///./src/router.js?");

/***/ }),

/***/ "./src/store/index.js":
/*!****************************!*\
  !*** ./src/store/index.js ***!
  \****************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var core_js_modules_es_array_find_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! core-js/modules/es.array.find.js */ \"./node_modules/core-js/modules/es.array.find.js\");\n/* harmony import */ var core_js_modules_es_array_find_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(core_js_modules_es_array_find_js__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var vuex__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! vuex */ \"./node_modules/vuex/dist/vuex.esm-browser.js\");\n\n\nvar availableLanguages = window.vueTranslationInterface.availableLanguages;\nvar store = Object(vuex__WEBPACK_IMPORTED_MODULE_1__[\"createStore\"])({\n  state: function state() {\n    return {\n      currentLanguage: null\n    };\n  },\n  getters: {\n    currentLanguage: function currentLanguage(state) {\n      return state.currentLanguage;\n    }\n  },\n  mutations: {\n    setLanguage: function setLanguage(state, payload) {\n      state.currentLanguage = payload;\n    }\n  },\n  actions: {\n    setLanguage: function setLanguage(context, payload) {\n      var language = availableLanguages.find(function (element) {\n        return element.pk === payload;\n      });\n      context.commit('setLanguage', language);\n    }\n  }\n});\n/* harmony default export */ __webpack_exports__[\"default\"] = (store);\n\n//# sourceURL=webpack:///./src/store/index.js?");

/***/ }),

/***/ 0:
/*!***************************!*\
  !*** multi ./src/main.js ***!
  \***************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

eval("module.exports = __webpack_require__(/*! ./src/main.js */\"./src/main.js\");\n\n\n//# sourceURL=webpack:///multi_./src/main.js?");

/***/ })

/******/ });