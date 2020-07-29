/* eslint-disable */(function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return c(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
/*
 * This file is part of Adblock Plus <https://adblockplus.org/>,
 * Copyright (C) 2006-present eyeo GmbH
 *
 * Adblock Plus is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 *
 * Adblock Plus is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Adblock Plus.  If not, see <http://www.gnu.org/licenses/>.
 */

"use strict";

function send(type, args)
{
  args = Object.assign({}, {type}, args);
  return browser.runtime.sendMessage(args);
}

const app = {
  get: (what) => send("app.get", {what}),
  open: (what) => send("app.open", {what})
};
module.exports.app = app;

const doclinks = {
  get: (link) => send("app.get", {what: "doclink", link})
};
module.exports.doclinks = doclinks;

const prefs = {
  get: (key) => send("prefs.get", {key})
};
module.exports.prefs = prefs;

const subscriptions = {
  getInitIssues: () => send("subscriptions.getInitIssues")
};
module.exports.subscriptions = subscriptions;

const stats = {
  getBlocked: (tab) => send("stats.getBlockedPerPage", {tab})
};
module.exports.stats = stats;

// For now we are merely reusing the port for long-lived communications to fix
// https://gitlab.com/eyeo/adblockplus/abpui/adblockplusui/issues/415
const port = browser.runtime.connect({name: "ui"});
module.exports.port = port;

},{}],2:[function(require,module,exports){
/*
 * This file is part of Adblock Plus <https://adblockplus.org/>,
 * Copyright (C) 2006-present eyeo GmbH
 *
 * Adblock Plus is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 *
 * Adblock Plus is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Adblock Plus.  If not, see <http://www.gnu.org/licenses/>.
 */

"use strict";

let browserName = "unknown";

// Firefox only, which is exactly the one
// we are looking for in order to patch events' layerX
if (browser.runtime.getBrowserInfo)
{
  browser.runtime.getBrowserInfo().then(info =>
  {
    browserName = info.name.toLowerCase();
  });
}

// used as legacy fallback in events.key(event) via keys[event.keyCode]
const keys = {
  9: "Tab",
  13: "Enter",
  27: "Escape",
  37: "ArrowLeft",
  38: "ArrowUp",
  39: "ArrowRight",
  40: "ArrowDown"
};

module.exports = {
  $: (selector, container = document) => container.querySelector(selector),
  $$: (selector, container = document) => container.querySelectorAll(selector),

  // helper to format as indented string any HTML/XML node
  asIndentedString,

  // basic copy and paste clipboard utility
  clipboard: {
    // warning: Firefox needs a proper event to work
    //          such click or mousedown or similar.
    copy(text)
    {
      const selection = document.getSelection();
      const selected = selection.rangeCount > 0 ?
                        selection.getRangeAt(0) : null;
      const el = document.createElement("textarea");
      el.value = text;
      el.setAttribute("readonly", "");
      el.style.cssText = "position:fixed;top:-999px";
      document.body.appendChild(el).select();
      document.execCommand("copy");
      document.body.removeChild(el);
      if (selected)
      {
        selection.removeAllRanges();
        // simply putting back selected doesn't work anymore
        const range = document.createRange();
        range.setStart(selected.startContainer, selected.startOffset);
        range.setEnd(selected.endContainer, selected.endOffset);
        selection.addRange(range);
      }
    },
    // optionally accepts a `paste` DOM event
    // it uses global clipboardData, if available, otherwise.
    // i.e. input.onpaste = event => console.log(dom.clipboard.paste(event));
    paste(event)
    {
      if (!event)
        event = window;
      const clipboardData = event.clipboardData || window.clipboardData;
      return clipboardData ? clipboardData.getData("text") : "";
    }
  },

  events: {
    // necessary to retrieve the right key before Chrome 51
    key(event)
    {
      return "key" in event ? event.key : keys[event.keyCode];
    }
  },

  // helper to provide the relative coordinates
  // to the closest positioned containing element
  relativeCoordinates(event)
  {
    // good old way that will work properly in older browsers too
    // mandatory for Chrome 49, still better than manual fallback
    // in all other browsers that provide such functionality
    let el = event.currentTarget;
    if ("layerX" in event && "layerY" in event)
    {
      let {layerX} = event;
      // see https://issues.adblockplus.org/ticket/7134
      if (browserName === "firefox")
        layerX -= el.offsetLeft;
      return {x: layerX, y: event.layerY};
    }
    // fallback when layerX/Y will be removed (since deprecated)
    let x = 0;
    let y = 0;
    do
    {
      x += el.offsetLeft - el.scrollLeft;
      y += el.offsetTop - el.scrollTop;
    } while (
      (el = el.offsetParent) &&
      !isNaN(el.offsetLeft) &&
      !isNaN(el.offsetTop)
    );
    return {x: event.pageX - x, y: event.pageY - y};
  }
};

function asIndentedString(element, indentation = 0)
{
  // only the first time it's called
  if (!indentation)
  {
    // get the top meaningful element to parse
    if (element.nodeType === 9)
      element = element.documentElement;
    // accept only elements
    if (element.nodeType !== 1)
      throw new Error("Unable to serialize " + element);
    // avoid original XML pollution at first iteration
    element = element.cloneNode(true);
  }
  const before = "  ".repeat(indentation + 1);
  const after = "  ".repeat(indentation);
  const doc = element.ownerDocument;
  const children = element.children;
  const length = children.length;
  for (let i = 0; i < length; i++)
  {
    const child = children[i];
    element.insertBefore(doc.createTextNode(`\n${before}`), child);
    asIndentedString(child, indentation + 1);
    if ((i + 1) === length)
      element.appendChild(doc.createTextNode(`\n${after}`));
  }
  // inner calls don't need to bother serialization
  if (indentation)
    return "";
  // easiest way to recognize an HTML element from an XML one
  if (/^https?:\/\/www\.w3\.org\/1999\/xhtml$/.test(element.namespaceURI))
    return element.outerHTML;
  // all other elements should use XML serializer
  return new XMLSerializer().serializeToString(element);
}

},{}],3:[function(require,module,exports){
/*
 * This file is part of Adblock Plus <https://adblockplus.org/>,
 * Copyright (C) 2006-present eyeo GmbH
 *
 * Adblock Plus is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 *
 * Adblock Plus is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Adblock Plus.  If not, see <http://www.gnu.org/licenses/>.
 */

"use strict";

const {wire, utils} = require("./io-element");
const {relativeCoordinates} = require("./dom");

// use native requestIdleCallback where available, fallback to setTimeout
const requestIdleCb = window.requestIdleCallback || setTimeout;

// at this point this is just a helper class
// for op-highlighter component but it could
// become a generic draw-on-canvas helper too
module.exports = class DrawingHandler
{
  constructor(canvas, maxSize)
  {
    this.paths = new Set();
    this.canvas = canvas;
    this.maxSize = maxSize;

    // the canvas needs proper width and height
    const canvasRect = canvas.getBoundingClientRect();
    canvas.width = canvasRect.width;
    canvas.height = canvasRect.height;

    // define a ratio that will produce an image with at least
    // 800px (maxSize) width and multiply by the device pixel ratio
    // to preserve the image quality on HiDPi screens.
    this.ratio = (maxSize / canvas.width) * (window.devicePixelRatio || 1);

    // it also needs to intercept all events
    if ("onpointerup" in canvas)
    {
      // the instance is the handler itself, no need to bind anything
      canvas.addEventListener("pointerdown", this, {passive: false});
      canvas.addEventListener("pointermove", this, {passive: false});
      canvas.addEventListener("pointerup", this, {passive: false});
      document.addEventListener("pointerup", this, {passive: false});
    }
    else
    {
      // some browser might not have pointer events.
      // the fallback should be regular mouse events
      this.onmousedown = this.onpointerdown;
      this.onmousemove = this.onpointermove;
      this.onmouseup = this.onpointerup;
      canvas.addEventListener("mousedown", this, {passive: false});
      canvas.addEventListener("mousemove", this, {passive: false});
      canvas.addEventListener("mouseup", this, {passive: false});
      document.addEventListener("mouseup", this, {passive: false});
    }
  }

  // draws an image and it starts processing its data
  // in an asynchronous, not CPU greedy, way.
  // It returns a promise that will resolve only
  // once the image has been fully processed.
  // Meanwhile, it is possible to draw rectangles on top.
  changeColorDepth(image)
  {
    this.clear();
    const {naturalWidth, naturalHeight} = image;
    const canvasWidth = this.canvas.width * this.ratio;
    const canvasHeight = (canvasWidth * naturalHeight) / naturalWidth;
    // resize the canvas to the displayed image size
    // to preserve HiDPi pixels
    this.canvas.width = canvasWidth;
    this.canvas.height = canvasHeight;
    // force its computed size in normal CSS pixels
    this.canvas.style.width = Math.round(canvasWidth / this.ratio) + "px";
    this.canvas.style.height = Math.round(canvasHeight / this.ratio) + "px";
    // draw resized image accordingly with new dimensions
    this.ctx.drawImage(image, 0, 0, naturalWidth, naturalHeight,
                              0, 0, canvasWidth, canvasHeight);
    // collect all info to process the iamge data
    this.imageData = this.ctx.getImageData(0, 0, canvasWidth, canvasHeight);
    const data = this.imageData.data;
    const length = data.length;
    const mapping = [0x00, 0x55, 0xAA, 0xFF];
    // don't loop all pixels at once, assuming devices
    // capable of HiDPi images have also enough power
    // to handle all those pixels.
    const avoidBlocking = Math.round(5000 * this.ratio);
    return new Promise(resolve =>
    {
      const remap = i =>
      {
        for (; i < length; i++)
        {
          data[i] = mapping[data[i] >> 6];
          if (i > 0 && i % avoidBlocking == 0)
          {
            notifyColorDepthChanges.call(this, i, length);
            // faster when possible, otherwise less intrusive
            // than a promise based on setTimeout as in legacy code
            return requestIdleCb(() =>
            {
              this.draw();
              requestIdleCb(() => remap(i + 1));
            });
          }
        }
        notifyColorDepthChanges.call(this, i, length);
        resolve();
      };
      remap(0);
    });
  }

  // setup the context the first time, and clean the area
  clear()
  {
    if (!this.ctx)
    {
      this.ctx = this.canvas.getContext("2d");
    }
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.ctx.lineJoin = "round";
    this.ctx.strokeStyle = "rgb(208, 1, 27)";
    this.ctx.fillStyle = "rgb(0, 0, 0)";
    this.ctx.lineWidth = 4 * this.ratio;
  }

  // draw the image during or after it's being processed
  // and draw on top all rectangles
  draw()
  {
    this.clear();
    if (this.imageData)
    {
      this.ctx.putImageData(this.imageData, 0, 0);
    }
    for (const rect of this.paths)
    {
      const method = `${rect.type}Rect`;
      this.ctx[method](
        rect.x * this.ratio,
        rect.y * this.ratio,
        rect.width * this.ratio,
        rect.height * this.ratio
      );
    }
  }

  // central event dispatcher
  // https://dom.spec.whatwg.org/#interface-eventtarget
  handleEvent(event)
  {
    this[`on${event.type}`](event);
  }

  // pointer events to draw on canvas
  onpointerdown(event)
  {
    // avoid multiple pointers/fingers
    if (this.drawing || !utils.event.isLeftClick(event))
      return;

    // react only if not drawing already
    stopEvent(event);
    this.drawing = true;
    const start = relativeCoordinates(event);
    // set current rect to speed up coordinates updates
    this.rect = {
      type: this.mode,
      x: start.x,
      y: start.y,
      width: 0,
      height: 0
    };
    this.paths.add(this.rect);
  }

  onpointermove(event)
  {
    // only if drawing
    if (!this.drawing)
      return;

    // update the current rect coordinates
    stopEvent(event);
    this.updateRect(event);
    // update the canvas view
    this.draw();
  }

  onpointerup(event)
  {
    // drop only if drawing
    // avoid issues when this event happens
    // outside the expected DOM node (or outside the browser)
    if (!this.drawing)
      return;

    stopEvent(event);
    if (event.currentTarget === this.canvas)
    {
      this.updateRect(event);
    }
    this.draw();
    this.drawing = false;

    // get out of here if the mouse didn't move at all
    if (!this.rect.width && !this.rect.height)
    {
      // also drop current rect from the list: it's useless.
      this.paths.delete(this.rect);
      return;
    }
    const rect = this.rect;
    const parent = this.canvas.parentNode;
    const closeCoords = getRelativeCoordinates(
      this.canvas,
      rect,
      {
        x: rect.x + rect.width,
        y: rect.y + rect.height
      }
    );

    // use the DOM to show the close event
    //  - always visible, even outside the canvas
    //  - no need to re-invent hit-test coordinates
    //  - no need to redraw without closers later on
    parent.appendChild(wire()`
      <span
        class="closer"
        onclick="${evt =>
        {
          if (!utils.event.isLeftClick(evt))
            return;
          // when clicked, remove the related rectangle
          // and draw the canvas again
          stopEvent(evt);
          parent.removeChild(evt.currentTarget);
          this.paths.delete(rect);
          this.draw();
        }}"
        style="${{
          // always top right corner
          top: closeCoords.y + "px",
          left: closeCoords.x + "px"
        }}"
      >
        <img src="/skin/icons/delete.svg" />
      </span>`);
  }

  // update current rectangle size
  updateRect(event)
  {
    const coords = relativeCoordinates(event);
    this.rect.width = coords.x - this.rect.x;
    this.rect.height = coords.y - this.rect.y;
  }
};

function notifyColorDepthChanges(value, max)
{
  const info = {detail: {value, max}};
  const ioHighlighter = this.canvas.closest("io-highlighter");
  ioHighlighter.dispatchEvent(new CustomEvent("changecolordepth", info));
}

// helper to retrieve absolute page coordinates
// of a generic target node
function getRelativeCoordinates(canvas, start, end)
{
  const x = Math.max(start.x, end.x) + canvas.offsetLeft;
  const y = Math.min(start.y, end.y) + canvas.offsetTop;
  return {x: Math.round(x), y: Math.round(y)};
}

// prevent events from doing anything
// in the current node, and every parent too
function stopEvent(event)
{
  event.preventDefault();
  event.stopPropagation();
}

},{"./dom":2,"./io-element":4}],4:[function(require,module,exports){
/*
 * This file is part of Adblock Plus <https://adblockplus.org/>,
 * Copyright (C) 2006-present eyeo GmbH
 *
 * Adblock Plus is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 *
 * Adblock Plus is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Adblock Plus.  If not, see <http://www.gnu.org/licenses/>.
 */

"use strict";

// Custom Elements ponyfill (a polyfill triggered on demand)
const customElementsPonyfill = require("document-register-element/pony");
if (typeof customElements !== "object")
  customElementsPonyfill(window);

// external dependencies
const {default: HyperHTMLElement} = require("hyperhtml-element/cjs");

// common DOM utilities exposed as IOElement.utils
const DOMUtils = {

  // boolean related operations/helpers
  boolean: {
    // utils.boolean.attribute(node, name, setAsTrue):void
    // set a generic node attribute name as "true"
    // if value is a boolean one or it removes the attribute
    attribute(node, name, setAsTrue)
    {
      // don't use `this.value(value)` with `this` as context
      // to make destructuring of helpers always work.
      // @example
      // const {attribute: setBoolAttr} = IOElement.utils.boolean;
      // setBoolAttr(node, 'test', true);
      if (DOMUtils.boolean.value(setAsTrue))
      {
        node.setAttribute(name, "true");
      }
      else
      {
        node.removeAttribute(name);
      }
    },

    // utils.boolean.value(any):boolean
    // it returns either true or false
    // via truthy or falsy values, but also via strings
    // representing "true", "false" as well as "0" or "1"
    value(value)
    {
      if (typeof value === "string" && value.length)
      {
        try
        {
          value = JSON.parse(value);
        }
        catch (error)
        {
          // Ignore invalid JSON to continue using value as string
        }
      }
      return !!value;
    }
  },

  event: {
    // returns true if it's a left click or a touch event.
    // The left mouse button value is 0 and this
    // is compatible with pointers/touch events
    // where `button` might not be there.
    isLeftClick(event)
    {
      const re = /^(?:click|mouse|touch|pointer)/;
      return re.test(event.type) && !event.button;
    }
  }
};

// provides a unique-id suffix per each component
let counter = 0;

// common Custom Element class to extend
class IOElement extends HyperHTMLElement
{
  // exposes DOM helpers as read only utils
  static get utils()
  {
    return DOMUtils;
  }

  // get a unique ID or, if null, set one and returns it
  static getID(element)
  {
    return element.getAttribute("id") || IOElement.setID(element);
  }

  // set a unique ID to a generic element and returns the ID
  static setID(element)
  {
    const id = `${element.nodeName.toLowerCase()}-${counter++}`;
    element.setAttribute("id", id);
    return id;
  }

  // lazily retrieve or define a custom element ID
  get id()
  {
    return IOElement.getID(this);
  }

  // returns true only when the component is live and styled
  get ready()
  {
    return !!this.offsetParent && this.isStyled();
  }

  // whenever an element is created, render its content once
  created() { this.render(); }

  // based on a `--component-name: ready;` convention
  // under the `component-name {}` related stylesheet,
  // this method returns true only if such stylesheet
  // has been already loaded.
  isStyled()
  {
    const computed = window.getComputedStyle(this, null);
    const property = "--" + this.nodeName.toLowerCase();
    // in some case Edge returns '#fff' instead of ready
    return computed.getPropertyValue(property).trim() !== "";
  }

  // by default, render is a no-op
  render() {}

  // usually a template would contain a main element such
  // input, button, div, section, etc.
  // having a simple way to retrieve such element can be
  // both semantic and handy, as opposite of using
  // this.children[0] each time
  get child()
  {
    let element = this.firstElementChild;
    // if accessed too early, will render automatically
    if (!element)
    {
      this.render();
      element = this.firstElementChild;
    }
    return element;
  }
}

// whenever an interpolation with ${{i18n: 'string-id'}} is found
// transform such value into the expected content
// example:
//  render() {
//    return this.html`<div>${{i18n:'about-abp'}}</div>`;
//  }
const {setElementText} = ext.i18n;
IOElement.intent("i18n", idOrArgs =>
{
  const fragment = document.createDocumentFragment();
  if (typeof idOrArgs === "string")
    setElementText(fragment, idOrArgs);
  else if (idOrArgs instanceof Array)
    setElementText(fragment, ...idOrArgs);
  return fragment;
});

module.exports = IOElement;

},{"document-register-element/pony":21,"hyperhtml-element/cjs":28}],5:[function(require,module,exports){
/*
 * This file is part of Adblock Plus <https://adblockplus.org/>,
 * Copyright (C) 2006-present eyeo GmbH
 *
 * Adblock Plus is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 *
 * Adblock Plus is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Adblock Plus.  If not, see <http://www.gnu.org/licenses/>.
 */

"use strict";

const IOElement = require("./io-element");
const DrawingHandler = require("./drawing-handler");

const {$} = require("./dom");

const {utils} = IOElement;

// <io-highlighter data-max-size=800 />
class IOHighlighter extends IOElement
{
  // define an initial state per each new instance
  // https://viperhtml.js.org/hyperhtml/documentation/#components-2
  get defaultState()
  {
    return {drawing: "", changeDepth: null};
  }

  // resolves once the image depth has been fully changed
  // comp.changeDepth.then(...)
  get changeDepth()
  {
    return this.state.changeDepth;
  }

  // returns true if there were hidden/highlighted areas
  get edited()
  {
    return this.drawingHandler ? this.drawingHandler.paths.size > 0 : false;
  }

  // process an image and setup changeDepth promise
  // returns the component for chainability sake
  // comp.edit(imageOrString).changeDepth.then(...);
  edit(source)
  {
    return this.setState({
      changeDepth: new Promise((res, rej) =>
      {
        const changeDepth = image =>
        {
          this.drawingHandler.changeColorDepth(image).then(res, rej);
        };

        if (typeof source === "string")
        {
          // create an image and use the source as data
          const img = this.ownerDocument.createElement("img");
          img.onload = () => changeDepth(img);
          img.onerror = rej;
          img.src = source;
        }
        else
        {
          // assume the source is an Image already
          // (or anything that can be drawn on a canvas)
          changeDepth(source);
        }
      })
    });
  }

  // the component content (invoked automatically on state change too)
  render()
  {
    if (this.state.drawing)
      this.setAttribute("drawing", this.state.drawing);
    else
      this.removeAttribute("drawing");

    this.html`
    <div class="split">
      <div class="options">
        <button
          tabindex="-1"
          class="highlight"
          onclick="${
            event =>
            {
              if (utils.event.isLeftClick(event))
                changeMode(this, "highlight");
            }
          }"
        >
          ${{i18n: "issueReporter_screenshot_highlight"}}
        </button>
        <button
          tabindex="-1"
          class="hide"
          onclick="${
            event =>
            {
              if (utils.event.isLeftClick(event))
                changeMode(this, "hide");
            }
          }"
        >
          ${{i18n: "issueReporter_screenshot_hide"}}
        </button>
      </div>
      <canvas />
    </div>`;

    // first time only, initialize the DrawingHandler
    // through the newly created canvas
    if (!this.drawingHandler)
      this.drawingHandler = new DrawingHandler(
        $("canvas", this),
        parseInt(this.dataset.maxSize, 10) || 800
      );
  }

  // shortcut for internal canvas.toDataURL()
  toDataURL()
  {
    return $("canvas", this).toDataURL();
  }
}

IOHighlighter.define("io-highlighter");

const changeMode = (self, mode) =>
{
  const drawing = self.state.drawing === mode ? "" : mode;
  self.drawingHandler.mode = mode === "hide" ? "fill" : "stroke";
  self.setState({drawing});
};

},{"./dom":2,"./drawing-handler":3,"./io-element":4}],6:[function(require,module,exports){
/*
 * This file is part of Adblock Plus <https://adblockplus.org/>,
 * Copyright (C) 2006-present eyeo GmbH
 *
 * Adblock Plus is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 *
 * Adblock Plus is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Adblock Plus.  If not, see <http://www.gnu.org/licenses/>.
 */

"use strict";

const IOElement = require("./io-element");

// a three steps example:
// <io-steps i18n-labels="first second third" />
class IOSteps extends IOElement
{
  static get observedAttributes()
  {
    return ["i18n-labels"];
  }

  created()
  {
    reset.call(this);
  }

  attributeChangedCallback()
  {
    // reset setup
    reset.call(this);
    // attributes can have spaces or new lines too
    for (const label of this.i18nLabels.split(/[\n ]+/))
    {
      const trimmed = label.trim();
      if (trimmed.length)
      {
        this.labels.push(browser.i18n.getMessage(trimmed));
      }
    }
    this.render();
  }

  // return the amount of enabled steps
  get enabled()
  {
    return this._enabled;
  }

  // return true or false accordingly if an index/step
  // has been already completed.
  getCompleted(index)
  {
    return index < this._enabled;
  }

  // set an index completed state
  // by default, completed is true
  setCompleted(index, completed = true)
  {
    if (index < 0)
      index = this.children.length + index;
    this.children[index].classList.toggle("completed", completed);
    if (
      completed &&
      index < this.labels.length &&
      this._enabled <= index
    )
    {
      this._enabled = index + 1;
      this.render();
    }
  }

  // dispatch a "step:click" event providing
  // the clicked index as event.detail property
  onclick(event)
  {
    event.preventDefault();
    event.stopPropagation();
    const indexOf = Array.prototype.indexOf;
    this.dispatchEvent(new CustomEvent("step:click", {
      bubbles: true,
      detail: indexOf.call(this.children, event.currentTarget)
    }));
  }

  render()
  {
    this.html`${this.labels.map(getButton, this)}`;
  }
}

const {wire} = IOElement;
function getButton(label, index)
{
  // each click dispatches change event
  // data-value is used to show the number
  return wire(this, `:${index}`)`
    <button
      onclick="${this}"
      disabled="${index > this._enabled}"
      data-value="${index + 1}"
    >${label}</button>`;
}

function reset()
{
  // amount of enabled lables, starts from at least one
  this._enabled = 0;
  // all the labels, passed as list
  this.labels = [];
}

IOSteps.define("io-steps");

},{"./io-element":4}],7:[function(require,module,exports){
/*
 * This file is part of Adblock Plus <https://adblockplus.org/>,
 * Copyright (C) 2006-present eyeo GmbH
 *
 * Adblock Plus is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 *
 * Adblock Plus is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Adblock Plus.  If not, see <http://www.gnu.org/licenses/>.
 */

"use strict";

const {port} = require("./api");
const {$, $$} = require("./dom");

const reportData = new DOMParser().parseFromString("<report></report>",
                                                 "text/xml");
let dataGatheringTabId = null;
let isMinimumTimeMet = false;

function getOriginalTabId()
{
  const tabId = parseInt(location.search.replace(/^\?/, ""), 10);
  if (!tabId && tabId !== 0)
    throw new Error("invalid tab id");

  return tabId;
}

port.onMessage.addListener((message) =>
{
  switch (message.type)
  {
    case "requests.respond":
      switch (message.action)
      {
        case "hits":
          const [request, filter, subscriptions] = message.args;
          const requestsContainerElem = $("requests", reportData);
          const filtersElem = $("filters", reportData);
          // ELEMHIDE hitLog request doesn't contain url
          if (request.url)
          {
            let requestElem = $(`[location="${request.url}"]`, reportData);
            if (requestElem)
            {
              const countNum = parseInt(
                requestElem.getAttribute("count"), 10
              );
              requestElem.setAttribute("count", countNum + 1);
            }
            else
            {
              requestElem = reportData.createElement("request");
              requestElem.setAttribute("location", censorURL(request.url));
              requestElem.setAttribute("type", request.type);
              requestElem.setAttribute("docDomain", request.docDomain);
              requestElem.setAttribute("thirdParty", request.thirdParty);
              requestElem.setAttribute("count", 1);
              requestsContainerElem.appendChild(requestElem);
            }
            if (filter)
              requestElem.setAttribute("filter", filter.text);
          }
          if (filter)
          {
            const existingFilter = $(`[text='${filter.text}']`, reportData);
            if (existingFilter)
            {
              const countNum = parseInt(existingFilter.getAttribute("hitCount"),
                                      10);
              existingFilter.setAttribute("hitCount", countNum + 1);
            }
            else
            {
              const filterElem = reportData.createElement("filter");
              filterElem.setAttribute("text", filter.text);
              filterElem.setAttribute("subscriptions", subscriptions.join(" "));
              filterElem.setAttribute("hitCount", 1);
              filtersElem.appendChild(filterElem);
            }
          }
          break;
      }
      break;
  }
});

module.exports = {
  closeRequestsCollectingTab,
  collectData()
  {
    let tabId;
    try
    {
      tabId = getOriginalTabId();
    }
    catch (ex)
    {
      return Promise.reject(ex);
    }

    return Promise.all([
      retrieveAddonInfo(),
      retrieveApplicationInfo(),
      retrievePlatformInfo(),
      retrieveWindowInfo(tabId),
      collectRequests(tabId),
      retrieveSubscriptions()
    ]).then(() => reportData);
  },
  updateConfigurationInfo
};

function collectRequests(tabId)
{
  reportData.documentElement.appendChild(reportData.createElement("requests"));
  reportData.documentElement.appendChild(reportData.createElement("filters"));
  return browser.tabs.get(tabId).then(tab =>
  {
    return browser.tabs.create({active: false, url: tab.url});
  }).then((tab) =>
  {
    dataGatheringTabId = tab.id;
    port.postMessage({
      type: "requests.listen",
      filter: ["hits"],
      tabId: dataGatheringTabId
    });

    function minimumTimeMet()
    {
      if (isMinimumTimeMet)
        return;

      isMinimumTimeMet = true;
      document.getElementById("showData").disabled = false;
      $("io-steps").dispatchEvent(new CustomEvent("requestcollected"));
      validateCommentsPage();
    }
    browser.tabs.onUpdated.addListener((updatedTabId, changeInfo) =>
    {
      if (updatedTabId == dataGatheringTabId && changeInfo.status == "complete")
        minimumTimeMet();
    });
    window.setTimeout(minimumTimeMet, 5000);
    window.addEventListener("beforeunload", (event) =>
    {
      closeRequestsCollectingTab();
    });
  });
}

let closedRequestsCollectingTab;
function closeRequestsCollectingTab()
{
  if (!closedRequestsCollectingTab)
    closedRequestsCollectingTab = browser.tabs.remove(dataGatheringTabId);

  return closedRequestsCollectingTab;
}

function retrieveAddonInfo()
{
  const element = reportData.createElement("adblock-plus");
  return browser.runtime.sendMessage({
    type: "app.get",
    what: "addonVersion"
  }).then(addonVersion =>
  {
    element.setAttribute("version", addonVersion);
    return browser.runtime.sendMessage({
      type: "app.get",
      what: "localeInfo"
    });
  }).then(({locale}) =>
  {
    element.setAttribute("locale", locale);
    reportData.documentElement.appendChild(element);
  });
}

function retrieveApplicationInfo()
{
  const element = reportData.createElement("application");
  return browser.runtime.sendMessage({
    type: "app.get",
    what: "application"
  }).then(application =>
  {
    element.setAttribute("name", capitalize(application));
    return browser.runtime.sendMessage({
      type: "app.get",
      what: "applicationVersion"
    });
  }).then(applicationVersion =>
  {
    element.setAttribute("version", applicationVersion);
    element.setAttribute("vendor", navigator.vendor);
    element.setAttribute("userAgent", navigator.userAgent);
    reportData.documentElement.appendChild(element);
  });
}

function retrievePlatformInfo()
{
  const element = reportData.createElement("platform");
  const {getBrowserInfo, sendMessage} = browser.runtime;
  return Promise.all([
    // Only Firefox supports browser.runtime.getBrowserInfo()
    (getBrowserInfo) ? getBrowserInfo() : null,
    sendMessage({
      type: "app.get",
      what: "platform"
    }),
    sendMessage({
      type: "app.get",
      what: "platformVersion"
    })
  ])
  .then(([browserInfo, platform, platformVersion]) =>
  {
    if (browserInfo)
    {
      element.setAttribute("build", browserInfo.buildID);
    }
    element.setAttribute("name", capitalize(platform));
    element.setAttribute("version", platformVersion);
    reportData.documentElement.appendChild(element);
  });
}

function retrieveWindowInfo(tabId)
{
  return browser.tabs.get(tabId)
    .then((tab) =>
    {
      let openerUrl = null;
      if (tab.openerTabId)
      {
        openerUrl = browser.tabs.get(tab.openerTabId)
          .then((openerTab) => openerTab.url);
      }

      const referrerUrl = browser.tabs.executeScript(tabId, {
        code: "document.referrer"
      })
      .then(([referrer]) => referrer);

      return Promise.all([tab.url, openerUrl, referrerUrl]);
    })
    .then(([url, openerUrl, referrerUrl]) =>
    {
      const element = reportData.createElement("window");
      if (openerUrl)
      {
        element.setAttribute("opener", censorURL(openerUrl));
      }
      if (referrerUrl)
      {
        element.setAttribute("referrer", censorURL(referrerUrl));
      }
      element.setAttribute("url", censorURL(url));
      reportData.documentElement.appendChild(element);
    });
}

function retrieveSubscriptions()
{
  return browser.runtime.sendMessage({
    type: "subscriptions.get",
    ignoreDisabled: true,
    downloadable: true,
    disabledFilters: true
  }).then(subscriptions =>
  {
    const element = reportData.createElement("subscriptions");
    for (const subscription of subscriptions)
    {
      if (!/^(http|https|ftp):/.test(subscription.url))
        continue;

      const now = Math.round(Date.now() / 1000);
      const subscriptionElement = reportData.createElement("subscription");
      subscriptionElement.setAttribute("id", subscription.url);
      if (subscription.version)
        subscriptionElement.setAttribute("version", subscription.version);
      if (subscription.lastDownload)
      {
        subscriptionElement.setAttribute("lastDownloadAttempt",
                                         subscription.lastDownload - now);
      }
      if (subscription.lastSuccess)
      {
        subscriptionElement.setAttribute("lastDownloadSuccess",
                                         subscription.lastSuccess - now);
      }
      if (subscription.softExpiration)
      {
        subscriptionElement.setAttribute("softExpiration",
                                         subscription.softExpiration - now);
      }
      if (subscription.expires)
      {
        subscriptionElement.setAttribute("hardExpiration",
                                         subscription.expires - now);
      }
      subscriptionElement.setAttribute("downloadStatus",
                                       subscription.downloadStatus);
      subscriptionElement.setAttribute("disabledFilters",
                                       subscription.disabledFilters.length);
      element.appendChild(subscriptionElement);
    }
    reportData.documentElement.appendChild(element);
  });
}

function setConfigurationInfo(configInfo)
{
  let extensionsContainer = $("extensions", reportData);
  let optionsContainer = $("options", reportData);

  if (!configInfo)
  {
    if (extensionsContainer)
    {
      extensionsContainer.parentNode.removeChild(extensionsContainer);
    }
    if (optionsContainer)
    {
      optionsContainer.parentNode.removeChild(optionsContainer);
    }
    return;
  }

  if (!extensionsContainer)
  {
    extensionsContainer = reportData.createElement("extensions");
    reportData.documentElement.appendChild(extensionsContainer);
  }
  if (!optionsContainer)
  {
    optionsContainer = reportData.createElement("options");
    reportData.documentElement.appendChild(optionsContainer);
  }

  extensionsContainer.innerHTML = "";
  optionsContainer.innerHTML = "";

  const {extensions, options} = configInfo;

  for (const id in options)
  {
    const element = reportData.createElement("option");
    element.setAttribute("id", id);
    element.textContent = options[id];
    optionsContainer.appendChild(element);
  }

  for (const extension of extensions)
  {
    const element = reportData.createElement("extension");
    element.setAttribute("id", extension.id);
    element.setAttribute("name", extension.name);
    element.setAttribute("type", extension.type);
    if (extension.version)
    {
      element.setAttribute("version", extension.version);
    }
    extensionsContainer.appendChild(element);
  }
}

// Chrome doesn't update the JavaScript context to reflect changes in the
// extension's permissions so we need to proxy our calls through a frame that
// loads after we request the necessary permissions
// https://bugs.chromium.org/p/chromium/issues/detail?id=594703
function proxyApiCall(apiId, ...args)
{
  return new Promise((resolve) =>
  {
    const iframe = document.createElement("iframe");
    iframe.hidden = true;
    iframe.src = browser.runtime.getURL("proxy.html");
    iframe.onload = () =>
    {
      function callback(...results)
      {
        document.body.removeChild(iframe);
        resolve(results[0]);
      }

      // The following APIs are injected at runtime so we can't rely on our
      // promise polyfill. Therefore we simplify things by proxying calls even
      // if the API has been made available to us in the same frame.
      const proxy = iframe.contentWindow.browser;
      switch (apiId)
      {
        case "contentSettings.cookies":
          if ("contentSettings" in proxy)
          {
            proxy.contentSettings.cookies.get(...args).then(callback);
          }
          else
          {
            callback(null);
          }
          break;
        case "contentSettings.javascript":
          if ("contentSettings" in proxy)
          {
            proxy.contentSettings.javascript.get(...args).then(callback);
          }
          else
          {
            callback(null);
          }
          break;
        case "management.getAll":
          if ("getAll" in proxy.management)
          {
            proxy.management.getAll(...args).then(callback);
          }
          else
          {
            callback(null);
          }
          break;
      }
    };
    document.body.appendChild(iframe);
  });
}

function retrieveExtensions()
{
  return proxyApiCall("management.getAll")
    .then((installed) =>
    {
      const extensions = [];

      for (const extension of installed)
      {
        if (!extension.enabled || extension.type != "extension")
          continue;

        extensions.push({
          id: extension.id,
          name: extension.name,
          type: "extension",
          version: extension.version
        });
      }

      const {plugins} = navigator;
      for (const plugin of plugins)
      {
        extensions.push({
          id: plugin.filename,
          name: plugin.name,
          type: "plugin"
        });
      }

      return extensions;
    })
    .catch((err) =>
    {
      console.error("Could not retrieve list of extensions");
      return [];
    });
}

function retrieveOptions()
{
  // Firefox doesn't support browser.contentSettings API
  if (!("contentSettings" in browser))
    return Promise.resolve({});

  let tabId;
  try
  {
    tabId = getOriginalTabId();
  }
  catch (ex)
  {
    return Promise.reject(ex);
  }

  return browser.tabs.get(tabId)
    .then((tab) =>
    {
      const details = {primaryUrl: tab.url, incognito: tab.incognito};

      return Promise.all([
        proxyApiCall("contentSettings.cookies", details),
        proxyApiCall("contentSettings.javascript", details),
        tab.incognito
      ]);
    })
    .then(([cookies, javascript, incognito]) =>
    {
      return {
        cookieBehavior: cookies.setting == "allow" ||
          cookies.setting == "session_only",
        javascript: javascript.setting == "allow",
        privateBrowsing: incognito
      };
    })
    .catch((err) =>
    {
      console.error("Could not retrieve configuration options");
      return {};
    });
}

function updateConfigurationInfo(isAccessible)
{
  if (!isAccessible)
  {
    setConfigurationInfo(null);
    return Promise.resolve();
  }

  return Promise.all([
    retrieveExtensions(),
    retrieveOptions()
  ])
  .then(([extensions, options]) =>
  {
    setConfigurationInfo({extensions, options});
  });
}

function capitalize(str)
{
  return str[0].toUpperCase() + str.slice(1);
}

function censorURL(url)
{
  return url.replace(/([?;&/#][^?;&/#]+?=)[^?;&/#]+/g, "$1*");
}

function setReportType(event)
{
  reportData.documentElement.setAttribute("type", event.target.value);
}

for (const typeElement of $$("#typeSelectorGroup input"))
{
  typeElement.addEventListener("change", setReportType);
}

let commentElement = null;
$("#comment").addEventListener("input", (event) =>
{
  const comment = event.target.value;
  if (!comment)
  {
    if (commentElement)
    {
      commentElement.parentNode.removeChild(commentElement);
      commentElement = null;
    }
  }
  else if (commentElement)
  {
    commentElement.textContent = comment;
  }
  else
  {
    commentElement = reportData.createElement("comment");
    commentElement.textContent = comment;
    reportData.documentElement.appendChild(commentElement);
  }
});

const anonSubmissionField = $("#anonymousSubmission");
const emailField = $("#email");
emailField.addEventListener("input", validateCommentsPage);
anonSubmissionField.addEventListener("click", validateCommentsPage);

const emailElement = reportData.createElement("email");
function validateCommentsPage()
{
  const sendButton = $("#send");
  $("#anonymousSubmissionWarning").setAttribute(
    "data-invisible",
    !anonSubmissionField.checked
  );
  if (anonSubmissionField.checked)
  {
    emailField.value = "";
    emailField.disabled = true;
    sendButton.disabled = !isMinimumTimeMet;
    if (emailElement.parentNode)
      emailElement.parentNode.removeChild(emailElement);
  }
  else
  {
    emailField.disabled = false;

    const value = emailField.value.trim();
    emailElement.textContent = value;
    reportData.documentElement.appendChild(emailElement);
    sendButton.disabled = (value == "" || !emailField.validity.valid ||
      !isMinimumTimeMet);
  }
  $("io-steps").dispatchEvent(
    new CustomEvent("formvalidated", {detail: !sendButton.disabled})
  );
}

},{"./api":1,"./dom":2}],8:[function(require,module,exports){
/*
 * This file is part of Adblock Plus <https://adblockplus.org/>,
 * Copyright (C) 2006-present eyeo GmbH
 *
 * Adblock Plus is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 *
 * Adblock Plus is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Adblock Plus.  If not, see <http://www.gnu.org/licenses/>.
 */

"use strict";

// both components are needed,
// and handled, by this file
require("./io-steps");
require("./io-highlighter");

const {$, $$} = require("./dom");

// managers are invoked right away
// but their initialization might be asynchronous
const managers = [
  // first screen, the welcome one
  // as soon as one radiobox is selected
  // the user can move forward
  ({ioSteps, page, index}) =>
  {
    page.addEventListener("change", event =>
    {
      ioSteps.setCompleted(index, true);
      enableContinue();
    });
  },

  // screenshot page, with highlight and hide ability
  // the canvas need to be visible to have a meaningful
  // computed with or height so the component itself
  // is injected only after the page has been selected
  // for the very first time only
  ({ioSteps, page, index, screenshot}) =>
  {
    // setup only first time is visible
    ioSteps.addEventListener("step:click", function once(event)
    {
      if (event.detail !== index)
        return;
      ioSteps.removeEventListener(event.type, once);
      const ioHighlighter = document.createElement("io-highlighter");
      page.appendChild(ioHighlighter);
      ioHighlighter.edit(screenshot);
      ioSteps.setCompleted(index, true);
      enableContinue();
    });
  },

  // third page, optional extra details where
  // the user can move on only if a valid email
  // is entered or the anonymous checkbox is used
  ({ioSteps, page, index}) =>
  {
    Promise.all([
      new Promise(resolve =>
      {
        ioSteps.addEventListener("requestcollected", resolve);
      }),
      new Promise(resolve =>
      {
        ioSteps.addEventListener("formvalidated", event =>
        {
          ioSteps.setCompleted(index, event.detail);
          $("button:last-child", ioSteps).disabled = true;
          if (event.detail)
            resolve();
        });
      })
    ]).then(() =>
    {
      $("#continue").hidden = true;
      $("#send").hidden = false;
    });
  },

  // last page, the sending of the report
  ({ioSteps, page, index, resolve}) =>
  {
    ioSteps.addEventListener("step:click", function once(event)
    {
      ioSteps.removeEventListener(event.type, once);
      const ioHighlighter = $("io-highlighter");
      ioHighlighter.changeDepth.then(() =>
      {
        resolve({
          screenshot:
          {
            get edited()
            {
              return ioHighlighter.edited;
            },
            get data()
            {
              return ioHighlighter.toDataURL();
            }
          }
        });
      });
    });
  }
];

module.exports = ({screenshot}) => new Promise(resolve =>
{
  const ioSteps = $("io-steps");
  const pages = $$("main > .page");
  const btnContinue = $("#continue");
  let currentPage = pages[0];
  let index = 0;
  ioSteps.addEventListener(
    "step:click",
    event =>
    {
      index = event.detail;
      const nextPage = pages[index];
      if (nextPage === currentPage)
        return;
      currentPage.hidden = true;
      currentPage = nextPage;
      currentPage.hidden = false;
      // allow users to click previous section that might be
      // already completed so that there's no reason to disable
      // the continue button
      btnContinue.disabled = !ioSteps.getCompleted(index);
    }
  );
  btnContinue.addEventListener(
    "click",
    event =>
    {
      ioSteps.dispatchEvent(
        new CustomEvent("step:click", {detail: index + 1})
      );
    }
  );
  managers.forEach((setup, i) =>
  {
    setup({ioSteps, page: pages[i], index: i, resolve, screenshot});
  });
});

function enableContinue()
{
  $("#continue").disabled = false;
}

},{"./dom":2,"./io-highlighter":5,"./io-steps":6}],9:[function(require,module,exports){
/*
 * This file is part of Adblock Plus <https://adblockplus.org/>,
 * Copyright (C) 2006-present eyeo GmbH
 *
 * Adblock Plus is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 *
 * Adblock Plus is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Adblock Plus.  If not, see <http://www.gnu.org/licenses/>.
 */

"use strict";

const stepsManager = require("./issue-reporter-steps-manager");
const report = require("./issue-reporter-report");
const {$, asIndentedString} = require("./dom");

const optionalPermissions = {
  permissions: [
    "contentSettings",
    "management"
  ]
};

function containsPermissions()
{
  // Firefox doesn't trigger the promise's catch() but instead throws
  try
  {
    return browser.permissions.contains(optionalPermissions);
  }
  catch (ex)
  {
    return Promise.reject(ex);
  }
}

document.addEventListener("DOMContentLoaded", () =>
{
  const supportEmail = "support@adblockplus.org";
  ext.i18n.setElementLinks(
    "sr-warning",
    `mailto:${supportEmail}`
  );
  ext.i18n.setElementLinks(
    "other-issues",
    `mailto:${supportEmail}?subject=${encodeURIComponent("[Issue Reporter]")}`
  );

  const cancelButton = $("#cancel");
  cancelButton.addEventListener("click", closeMe);
  $("#hide-notification").addEventListener("click", () =>
  {
    $("#notification").setAttribute("aria-hidden", true);
  });

  const collectedData = report.collectData().catch(e =>
  {
    console.error(e);
    alert(e);
    closeMe();
  });

  const manageSteps = browser.tabs.captureVisibleTab(null, {format: "png"})
    .then(screenshot =>
    {
      // activate current tab and let the user report
      return browser.tabs.getCurrent()
        .then(tab => browser.tabs.update(tab.id, {active: true}))
        .then(() => stepsManager({screenshot}));
    });

  $("#send").addEventListener("click", function sendAll(event)
  {
    const sendButton = event.currentTarget;
    const lastStep = $("io-steps button:last-child");
    sendButton.removeEventListener("click", sendAll);
    sendButton.disabled = true;
    lastStep.disabled = false;
    lastStep.click();
    $("io-highlighter").addEventListener("changecolordepth", evt =>
    {
      const progress = $("#sendingProgress");
      const {max, value} = evt.detail;
      // do not fulfill the bar with this info only
      // the idea is to show a general progress for
      // both the color depth and the sending report
      progress.max = max * 2;
      progress.value = value;
    });
    Promise.all([collectedData, manageSteps]).then(results =>
    {
      // At this point the report is sent,
      // and there will be a link within an iframe
      // that navigates, within the same page, to the
      // reported issue online.
      // Without removing the beforeunload callback,
      // and because the page is the current tab,
      // the user won't be able to reach the report,
      // because the tab itself would close instead.
      window.removeEventListener("beforeunload", closeMe);
      cancelButton.disabled = true;
      cancelButton.hidden = true;
      sendReport(reportWithScreenshot(...results));
      sendButton.textContent =
        browser.i18n.getMessage("issueReporter_closeButton_label");
      $("io-steps").setCompleted(-1, true);
    });
  });

  // We query our permissions here to find out whether the browser supports them
  containsPermissions()
    .then(() =>
    {
      const includeConfig = $("#includeConfig");
      includeConfig.addEventListener("change", (event) =>
      {
        if (!includeConfig.checked)
        {
          report.updateConfigurationInfo(false);
          return;
        }

        event.preventDefault();

        browser.permissions.request(optionalPermissions)
          .then((granted) =>
          {
            return report.updateConfigurationInfo(granted)
              .then(() =>
              {
                includeConfig.checked = granted;
              });
          })
          // Catch error here already to ensure permission is removed
          // even if we are unable to update the report data
          .catch(console.error)
          .then(() => browser.permissions.remove(optionalPermissions))
          .then((success) =>
          {
            if (!success)
              throw new Error("Failed to remove permissions");
          })
          .catch(console.error);
      });
    })
    .catch((err) =>
    {
      // No need to ask for more data if we won't be able to access it anyway
      const includeConfig = $("#includeConfigContainer");
      includeConfig.hidden = true;
    });

  const showDataOverlay = $("#showDataOverlay");
  $("#showData").addEventListener("click", event =>
  {
    event.preventDefault();

    collectedData.then(
      xmlReport =>
      {
        report.closeRequestsCollectingTab().then(() =>
        {
          showDataOverlay.hidden = false;

          reportWithScreenshot(xmlReport, {screenshot: $("io-highlighter")});
          const element = $("#showDataValue");
          element.textContent = asIndentedString(xmlReport);
          element.focus();
        });
      }
    );
  });
  $("#showDataClose").addEventListener("click", event =>
  {
    showDataOverlay.hidden = true;
    $("#showData").focus();
  });
});

let notifyClosing = true;
window.addEventListener("beforeunload", closeMe);
function closeMe()
{
  if (notifyClosing)
  {
    notifyClosing = false;
    browser.runtime.sendMessage({
      type: "app.get",
      what: "senderId"
    }).then(tabId => browser.tabs.remove(tabId));
  }
}

function reportWithScreenshot(xmlReport, stepsData)
{
  const {edited, data} = stepsData.screenshot;
  const element = $("screenshot", xmlReport.documentElement) ||
                  xmlReport.createElement("screenshot");
  element.setAttribute("edited", edited);
  const proc = browser.i18n.getMessage("issueReporter_processing_screenshot");
  element.textContent = data || `data:image/png;base64,...${proc}...`;
  xmlReport.documentElement.appendChild(element);
  return xmlReport;
}

function generateUUID(size = 8)
{
  const uuid = new Uint16Array(size);
  window.crypto.getRandomValues(uuid);
  uuid[3] = uuid[3] & 0x0FFF | 0x4000;  // version 4
  uuid[4] = uuid[4] & 0x3FFF | 0x8000;  // variant 1

  const uuidChunks = [];
  for (let i = 0; i < uuid.length; i++)
  {
    const component = uuid[i].toString(16);
    uuidChunks.push(("000" + component).slice(-4));
    if (i >= 1 && i <= 4)
      uuidChunks.push("-");
  }
  return uuidChunks.join("");
}

function sendReport(reportData)
{
  // Passing a sequence to URLSearchParams() constructor only works starting
  // with Firefox 53, add values "manually" for now.
  const params = new URLSearchParams();
  for (const [param, value] of [
    ["version", 1],
    ["guid", generateUUID()],
    ["lang", $("adblock-plus", reportData)
                       .getAttribute("locale")]
  ])
  {
    params.append(param, value);
  }

  const url = "https://reports.adblockplus.org/submitReport?" + params;

  const reportSent = event =>
  {
    let success = false;
    let errorMessage = browser.i18n.getMessage(
      "filters_subscription_lastDownload_connectionError"
    );
    try
    {
      success = request.status == 200;
      if (request.status != 0)
        errorMessage = request.status + " " + request.statusText;
    }
    catch (e)
    {
      // Getting request status might throw if no connection was established
    }

    let result;
    try
    {
      result = request.responseText;
    }
    catch (e)
    {
      result = "";
    }

    if (!success)
    {
      const errorElement = document.getElementById("error");
      const template = browser.i18n.getMessage("issueReporter_errorMessage")
                                    .replace(/[\r\n\s]+/g, " ");

      const [, before, linkText, after] =
              /(.*)\[link\](.*)\[\/link\](.*)/.exec(template) ||
              [null, "", template, ""];
      const beforeLink = before.replace(/\?1\?/g, errorMessage);
      const afterLink = after.replace(/\?1\?/g, errorMessage);

      while (errorElement.firstChild)
        errorElement.removeChild(errorElement.firstChild);

      const link = document.createElement("a");
      link.textContent = linkText;
      browser.runtime.sendMessage({
        type: "app.get",
        what: "doclink",
        link: "reporter_connect_issue"
      }).then(supportUrl =>
      {
        link.href = supportUrl;
      });


      errorElement.appendChild(document.createTextNode(beforeLink));
      errorElement.appendChild(link);
      errorElement.appendChild(document.createTextNode(afterLink));

      errorElement.hidden = false;
    }

    result = result.replace(/%CONFIRMATION%/g, encodeHTML(
                browser.i18n.getMessage("issueReporter_confirmationMessage")
              ));
    result = result.replace(/%KNOWNISSUE%/g, encodeHTML(
                browser.i18n.getMessage("issueReporter_knownIssueMessage")
              ));
    result = result.replace(/(<html)\b/, '$1 dir="' + encodeHTML(
                window.getComputedStyle(
                  document.documentElement, ""
                ).direction + '"'
              ));

    document.getElementById("sendReportMessage").hidden = true;
    document.getElementById("sendingProgressContainer").hidden = true;

    const resultFrame = document.getElementById("result");
    resultFrame.setAttribute("src", "data:text/html;charset=utf-8," +
                                    encodeURIComponent(result));
    resultFrame.hidden = false;

    document.getElementById("continue").disabled = false;

    if (success)
    {
      $("#send").disabled = false;
      $("#send").addEventListener("click", closeMe);
    }
  };

  const request = new XMLHttpRequest();
  request.open("POST", url);
  request.setRequestHeader("Content-Type", "text/xml");
  request.setRequestHeader("X-Adblock-Plus", "1");
  request.addEventListener("load", reportSent);
  request.addEventListener("error", reportSent);
  const progress = document.getElementById("sendingProgress");
  request.upload.addEventListener("progress", event =>
  {
    if (!event.lengthComputable)
      return;

    if (event.loaded > 0)
    {
      // normalize the ratio between previous loading and the current one
      // previous one stopped at 50, so it starts from 50
      progress.max = 100;
      progress.value = 50 + (50 * event.loaded) / event.total;
    }
  });
  request.send(asIndentedString(reportData));
}

function encodeHTML(str)
{
  return str.replace(/[&<>"]/g, c => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;"
  }[c]));
}

},{"./dom":2,"./issue-reporter-report":7,"./issue-reporter-steps-manager":8}],10:[function(require,module,exports){
/*! (c) Andrea Giammarchi - ISC */
var createContent = (function (document) {'use strict';
  var FRAGMENT = 'fragment';
  var TEMPLATE = 'template';
  var HAS_CONTENT = 'content' in create(TEMPLATE);

  var createHTML = HAS_CONTENT ?
    function (html) {
      var template = create(TEMPLATE);
      template.innerHTML = html;
      return template.content;
    } :
    function (html) {
      var content = create(FRAGMENT);
      var template = create(TEMPLATE);
      var childNodes = null;
      if (/^[^\S]*?<(col(?:group)?|t(?:head|body|foot|r|d|h))/i.test(html)) {
        var selector = RegExp.$1;
        template.innerHTML = '<table>' + html + '</table>';
        childNodes = template.querySelectorAll(selector);
      } else {
        template.innerHTML = html;
        childNodes = template.childNodes;
      }
      append(content, childNodes);
      return content;
    };

  return function createContent(markup, type) {
    return (type === 'svg' ? createSVG : createHTML)(markup);
  };

  function append(root, childNodes) {
    var length = childNodes.length;
    while (length--)
      root.appendChild(childNodes[0]);
  }

  function create(element) {
    return element === FRAGMENT ?
      document.createDocumentFragment() :
      document.createElementNS('http://www.w3.org/1999/xhtml', element);
  }

  // it could use createElementNS when hasNode is there
  // but this fallback is equally fast and easier to maintain
  // it is also battle tested already in all IE
  function createSVG(svg) {
    var content = create(FRAGMENT);
    var template = create('div');
    template.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg">' + svg + '</svg>';
    append(content, template.firstChild.childNodes);
    return content;
  }

}(document));
module.exports = createContent;

},{}],11:[function(require,module,exports){
/*! (c) Andrea Giammarchi - ISC */
var self = this || /* istanbul ignore next */ {};
self.CustomEvent = typeof CustomEvent === 'function' ?
  CustomEvent :
  (function (__p__) {
    CustomEvent[__p__] = new CustomEvent('').constructor[__p__];
    return CustomEvent;
    function CustomEvent(type, init) {
      if (!init) init = {};
      var e = document.createEvent('CustomEvent');
      e.initCustomEvent(type, !!init.bubbles, !!init.cancelable, init.detail);
      return e;
    }
  }('prototype'));
module.exports = self.CustomEvent;

},{}],12:[function(require,module,exports){
/*! (c) Andrea Giammarchi - ISC */
var self = this || /* istanbul ignore next */ {};
try { self.Map = Map; }
catch (Map) {
  self.Map = function Map() {
    var i = 0;
    var k = [];
    var v = [];
    return {
      delete: function (key) {
        var had = contains(key);
        if (had) {
          k.splice(i, 1);
          v.splice(i, 1);
        }
        return had;
      },
      forEach: function forEach(callback, context) {
        k.forEach(
          function (key, i)  {
            callback.call(context, v[i], key, this);
          },
          this
        );
      },
      get: function get(key) {
        return contains(key) ? v[i] : void 0;
      },
      has: function has(key) {
        return contains(key);
      },
      set: function set(key, value) {
        v[contains(key) ? i : (k.push(key) - 1)] = value;
        return this;
      }
    };
    function contains(v) {
      i = k.indexOf(v);
      return -1 < i;
    }
  };
}
module.exports = self.Map;

},{}],13:[function(require,module,exports){
/*! (c) Andrea Giammarchi - ISC */
var self = this || /* istanbul ignore next */ {};
try { self.WeakSet = WeakSet; }
catch (WeakSet) {
  (function (id, dP) {
    var proto = WeakSet.prototype;
    proto.add = function (object) {
      if (!this.has(object))
        dP(object, this._, {value: true, configurable: true});
      return this;
    };
    proto.has = function (object) {
      return this.hasOwnProperty.call(object, this._);
    };
    proto.delete = function (object) {
      return this.has(object) && delete object[this._];
    };
    self.WeakSet = WeakSet;
    function WeakSet() {'use strict';
      dP(this, '_', {value: '_@ungap/weakmap' + id++});
    }
  }(Math.random(), Object.defineProperty));
}
module.exports = self.WeakSet;

},{}],14:[function(require,module,exports){
/*! (c) Andrea Giammarchi - ISC */
var importNode = (function (
  document,
  appendChild,
  cloneNode,
  createTextNode,
  importNode
) {
  var native = importNode in document;
  // IE 11 has problems with cloning templates:
  // it "forgets" empty childNodes. This feature-detects that.
  var fragment = document.createDocumentFragment();
  fragment[appendChild](document[createTextNode]('g'));
  fragment[appendChild](document[createTextNode](''));
  var content = native ?
    document[importNode](fragment, true) :
    fragment[cloneNode](true);
  return content.childNodes.length < 2 ?
    function importNode(node, deep) {
      var clone = node[cloneNode]();
      for (var
        childNodes = node.childNodes || [],
        length = childNodes.length,
        i = 0; deep && i < length; i++
      ) {
        clone[appendChild](importNode(childNodes[i], deep));
      }
      return clone;
    } :
    (native ?
      document[importNode] :
      function (node, deep) {
        return node[cloneNode](!!deep);
      }
    );
}(
  document,
  'appendChild',
  'cloneNode',
  'createTextNode',
  'importNode'
));
module.exports = importNode;

},{}],15:[function(require,module,exports){
var isArray = Array.isArray || (function (toString) {
  var $ = toString.call([]);
  return function isArray(object) {
    return toString.call(object) === $;
  };
}({}.toString));
module.exports = isArray;

},{}],16:[function(require,module,exports){
'use strict';
const WeakMap = (require('@ungap/weakmap'));

var isNoOp = typeof document !== 'object';

var templateLiteral = function (tl) {
  var RAW = 'raw';
  var isBroken = function (UA) {
    return /(Firefox|Safari)\/(\d+)/.test(UA) &&
          !/(Chrom[eium]+|Android)\/(\d+)/.test(UA);
  };
  var broken = isBroken((document.defaultView.navigator || {}).userAgent);
  var FTS = !(RAW in tl) ||
            tl.propertyIsEnumerable(RAW) ||
            !Object.isFrozen(tl[RAW]);
  if (broken || FTS) {
    var forever = {};
    var foreverCache = function (tl) {
      for (var key = '.', i = 0; i < tl.length; i++)
        key += tl[i].length + '.' + tl[i];
      return forever[key] || (forever[key] = tl);
    };
    // Fallback TypeScript shenanigans
    if (FTS)
      templateLiteral = foreverCache;
    // try fast path for other browsers:
    // store the template as WeakMap key
    // and forever cache it only when it's not there.
    // this way performance is still optimal,
    // penalized only when there are GC issues
    else {
      var wm = new WeakMap;
      var set = function (tl, unique) {
        wm.set(tl, unique);
        return unique;
      };
      templateLiteral = function (tl) {
        return wm.get(tl) || set(tl, foreverCache(tl));
      };
    }
  } else {
    isNoOp = true;
  }
  return TL(tl);
};

module.exports = TL;

function TL(tl) {
  return isNoOp ? tl : templateLiteral(tl);
}

},{"@ungap/weakmap":19}],17:[function(require,module,exports){
'use strict';
const unique = (require('@ungap/template-literal'));

Object.defineProperty(exports, '__esModule', {value: true}).default = function (template) {
  var length = arguments.length;
  var args = [unique(template)];
  var i = 1;
  while (i < length)
    args.push(arguments[i++]);
  return args;
};

},{"@ungap/template-literal":16}],18:[function(require,module,exports){
var trim = ''.trim || function () {
  return String(this).replace(/^\s+|\s+/g, '');
};
module.exports = trim;

},{}],19:[function(require,module,exports){
/*! (c) Andrea Giammarchi - ISC */
var self = this || /* istanbul ignore next */ {};
try { self.WeakMap = WeakMap; }
catch (WeakMap) {
  // this could be better but 90% of the time
  // it's everything developers need as fallback
  self.WeakMap = (function (id, Object) {'use strict';
    var dP = Object.defineProperty;
    var hOP = Object.hasOwnProperty;
    var proto = WeakMap.prototype;
    proto.delete = function (key) {
      return this.has(key) && delete key[this._];
    };
    proto.get = function (key) {
      return this.has(key) ? key[this._] : void 0;
    };
    proto.has = function (key) {
      return hOP.call(key, this._);
    };
    proto.set = function (key, value) {
      dP(key, this._, {configurable: true, value: value});
      return this;
    };
    return WeakMap;
    function WeakMap(iterable) {
      dP(this, '_', {value: '_@ungap/weakmap' + id++});
      if (iterable)
        iterable.forEach(add, this);
    }
    function add(pair) {
      this.set(pair[0], pair[1]);
    }
  }(Math.random(), Object));
}
module.exports = self.WeakMap;

},{}],20:[function(require,module,exports){
/*! (c) Andrea Giammarchi */
function disconnected(poly) {'use strict';
  var Event = poly.Event;
  var WeakSet = poly.WeakSet;
  var notObserving = true;
  var observer = null;
  return function observe(node) {
    if (notObserving) {
      notObserving = !notObserving;
      observer = new WeakSet;
      startObserving(node.ownerDocument);
    }
    observer.add(node);
    return node;
  };
  function startObserving(document) {
    var connected = new WeakSet;
    var disconnected = new WeakSet;
    try {
      (new MutationObserver(changes)).observe(
        document,
        {subtree: true, childList: true}
      );
    }
    catch(o_O) {
      var timer = 0;
      var records = [];
      var reschedule = function (record) {
        records.push(record);
        clearTimeout(timer);
        timer = setTimeout(
          function () {
            changes(records.splice(timer = 0, records.length));
          },
          0
        );
      };
      document.addEventListener(
        'DOMNodeRemoved',
        function (event) {
          reschedule({addedNodes: [], removedNodes: [event.target]});
        },
        true
      );
      document.addEventListener(
        'DOMNodeInserted',
        function (event) {
          reschedule({addedNodes: [event.target], removedNodes: []});
        },
        true
      );
    }
    function changes(records) {
      for (var
        record,
        length = records.length,
        i = 0; i < length; i++
      ) {
        record = records[i];
        dispatchAll(record.removedNodes, 'disconnected', disconnected, connected);
        dispatchAll(record.addedNodes, 'connected', connected, disconnected);
      }
    }
    function dispatchAll(nodes, type, wsin, wsout) {
      for (var
        node,
        event = new Event(type),
        length = nodes.length,
        i = 0; i < length;
        (node = nodes[i++]).nodeType === 1 &&
        dispatchTarget(node, event, type, wsin, wsout)
      );
    }
    function dispatchTarget(node, event, type, wsin, wsout) {
      if (observer.has(node) && !wsin.has(node)) {
        wsout.delete(node);
        wsin.add(node);
        node.dispatchEvent(event);
        /*
        // The event is not bubbling (perf reason: should it?),
        // hence there's no way to know if
        // stop/Immediate/Propagation() was called.
        // Should DOM Level 0 work at all?
        // I say it's a YAGNI case for the time being,
        // and easy to implement in user-land.
        if (!event.cancelBubble) {
          var fn = node['on' + type];
          if (fn)
            fn.call(node, event);
        }
        */
      }
      for (var
        // apparently is node.children || IE11 ... ^_^;;
        // https://github.com/WebReflection/disconnected/issues/1
        children = node.children || [],
        length = children.length,
        i = 0; i < length;
        dispatchTarget(children[i++], event, type, wsin, wsout)
      );
    }
  }
}
module.exports = disconnected;

},{}],21:[function(require,module,exports){
/*!
ISC License

Copyright (c) 2014-2018, Andrea Giammarchi, @WebReflection

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.

*/
// global window Object
// optional polyfill info
//    'auto' used by default, everything is feature detected
//    'force' use the polyfill even if not fully needed
function installCustomElements(window, polyfill) {'use strict';

  // DO NOT USE THIS FILE DIRECTLY, IT WON'T WORK
  // THIS IS A PROJECT BASED ON A BUILD SYSTEM
  // THIS FILE IS JUST WRAPPED UP RESULTING IN
  // build/document-register-element.node.js

  var
    document = window.document,
    Object = window.Object
  ;

  var htmlClass = (function (info) {
    // (C) Andrea Giammarchi - @WebReflection - MIT Style
    var
      catchClass = /^[A-Z]+[a-z]/,
      filterBy = function (re) {
        var arr = [], tag;
        for (tag in register) {
          if (re.test(tag)) arr.push(tag);
        }
        return arr;
      },
      add = function (Class, tag) {
        tag = tag.toLowerCase();
        if (!(tag in register)) {
          register[Class] = (register[Class] || []).concat(tag);
          register[tag] = (register[tag.toUpperCase()] = Class);
        }
      },
      register = (Object.create || Object)(null),
      htmlClass = {},
      i, section, tags, Class
    ;
    for (section in info) {
      for (Class in info[section]) {
        tags = info[section][Class];
        register[Class] = tags;
        for (i = 0; i < tags.length; i++) {
          register[tags[i].toLowerCase()] =
          register[tags[i].toUpperCase()] = Class;
        }
      }
    }
    htmlClass.get = function get(tagOrClass) {
      return typeof tagOrClass === 'string' ?
        (register[tagOrClass] || (catchClass.test(tagOrClass) ? [] : '')) :
        filterBy(tagOrClass);
    };
    htmlClass.set = function set(tag, Class) {
      return (catchClass.test(tag) ?
        add(tag, Class) :
        add(Class, tag)
      ), htmlClass;
    };
    return htmlClass;
  }({
    "collections": {
      "HTMLAllCollection": [
        "all"
      ],
      "HTMLCollection": [
        "forms"
      ],
      "HTMLFormControlsCollection": [
        "elements"
      ],
      "HTMLOptionsCollection": [
        "options"
      ]
    },
    "elements": {
      "Element": [
        "element"
      ],
      "HTMLAnchorElement": [
        "a"
      ],
      "HTMLAppletElement": [
        "applet"
      ],
      "HTMLAreaElement": [
        "area"
      ],
      "HTMLAttachmentElement": [
        "attachment"
      ],
      "HTMLAudioElement": [
        "audio"
      ],
      "HTMLBRElement": [
        "br"
      ],
      "HTMLBaseElement": [
        "base"
      ],
      "HTMLBodyElement": [
        "body"
      ],
      "HTMLButtonElement": [
        "button"
      ],
      "HTMLCanvasElement": [
        "canvas"
      ],
      "HTMLContentElement": [
        "content"
      ],
      "HTMLDListElement": [
        "dl"
      ],
      "HTMLDataElement": [
        "data"
      ],
      "HTMLDataListElement": [
        "datalist"
      ],
      "HTMLDetailsElement": [
        "details"
      ],
      "HTMLDialogElement": [
        "dialog"
      ],
      "HTMLDirectoryElement": [
        "dir"
      ],
      "HTMLDivElement": [
        "div"
      ],
      "HTMLDocument": [
        "document"
      ],
      "HTMLElement": [
        "element",
        "abbr",
        "address",
        "article",
        "aside",
        "b",
        "bdi",
        "bdo",
        "cite",
        "code",
        "command",
        "dd",
        "dfn",
        "dt",
        "em",
        "figcaption",
        "figure",
        "footer",
        "header",
        "i",
        "kbd",
        "mark",
        "nav",
        "noscript",
        "rp",
        "rt",
        "ruby",
        "s",
        "samp",
        "section",
        "small",
        "strong",
        "sub",
        "summary",
        "sup",
        "u",
        "var",
        "wbr"
      ],
      "HTMLEmbedElement": [
        "embed"
      ],
      "HTMLFieldSetElement": [
        "fieldset"
      ],
      "HTMLFontElement": [
        "font"
      ],
      "HTMLFormElement": [
        "form"
      ],
      "HTMLFrameElement": [
        "frame"
      ],
      "HTMLFrameSetElement": [
        "frameset"
      ],
      "HTMLHRElement": [
        "hr"
      ],
      "HTMLHeadElement": [
        "head"
      ],
      "HTMLHeadingElement": [
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6"
      ],
      "HTMLHtmlElement": [
        "html"
      ],
      "HTMLIFrameElement": [
        "iframe"
      ],
      "HTMLImageElement": [
        "img"
      ],
      "HTMLInputElement": [
        "input"
      ],
      "HTMLKeygenElement": [
        "keygen"
      ],
      "HTMLLIElement": [
        "li"
      ],
      "HTMLLabelElement": [
        "label"
      ],
      "HTMLLegendElement": [
        "legend"
      ],
      "HTMLLinkElement": [
        "link"
      ],
      "HTMLMapElement": [
        "map"
      ],
      "HTMLMarqueeElement": [
        "marquee"
      ],
      "HTMLMediaElement": [
        "media"
      ],
      "HTMLMenuElement": [
        "menu"
      ],
      "HTMLMenuItemElement": [
        "menuitem"
      ],
      "HTMLMetaElement": [
        "meta"
      ],
      "HTMLMeterElement": [
        "meter"
      ],
      "HTMLModElement": [
        "del",
        "ins"
      ],
      "HTMLOListElement": [
        "ol"
      ],
      "HTMLObjectElement": [
        "object"
      ],
      "HTMLOptGroupElement": [
        "optgroup"
      ],
      "HTMLOptionElement": [
        "option"
      ],
      "HTMLOutputElement": [
        "output"
      ],
      "HTMLParagraphElement": [
        "p"
      ],
      "HTMLParamElement": [
        "param"
      ],
      "HTMLPictureElement": [
        "picture"
      ],
      "HTMLPreElement": [
        "pre"
      ],
      "HTMLProgressElement": [
        "progress"
      ],
      "HTMLQuoteElement": [
        "blockquote",
        "q",
        "quote"
      ],
      "HTMLScriptElement": [
        "script"
      ],
      "HTMLSelectElement": [
        "select"
      ],
      "HTMLShadowElement": [
        "shadow"
      ],
      "HTMLSlotElement": [
        "slot"
      ],
      "HTMLSourceElement": [
        "source"
      ],
      "HTMLSpanElement": [
        "span"
      ],
      "HTMLStyleElement": [
        "style"
      ],
      "HTMLTableCaptionElement": [
        "caption"
      ],
      "HTMLTableCellElement": [
        "td",
        "th"
      ],
      "HTMLTableColElement": [
        "col",
        "colgroup"
      ],
      "HTMLTableElement": [
        "table"
      ],
      "HTMLTableRowElement": [
        "tr"
      ],
      "HTMLTableSectionElement": [
        "thead",
        "tbody",
        "tfoot"
      ],
      "HTMLTemplateElement": [
        "template"
      ],
      "HTMLTextAreaElement": [
        "textarea"
      ],
      "HTMLTimeElement": [
        "time"
      ],
      "HTMLTitleElement": [
        "title"
      ],
      "HTMLTrackElement": [
        "track"
      ],
      "HTMLUListElement": [
        "ul"
      ],
      "HTMLUnknownElement": [
        "unknown",
        "vhgroupv",
        "vkeygen"
      ],
      "HTMLVideoElement": [
        "video"
      ]
    },
    "nodes": {
      "Attr": [
        "node"
      ],
      "Audio": [
        "audio"
      ],
      "CDATASection": [
        "node"
      ],
      "CharacterData": [
        "node"
      ],
      "Comment": [
        "#comment"
      ],
      "Document": [
        "#document"
      ],
      "DocumentFragment": [
        "#document-fragment"
      ],
      "DocumentType": [
        "node"
      ],
      "HTMLDocument": [
        "#document"
      ],
      "Image": [
        "img"
      ],
      "Option": [
        "option"
      ],
      "ProcessingInstruction": [
        "node"
      ],
      "ShadowRoot": [
        "#shadow-root"
      ],
      "Text": [
        "#text"
      ],
      "XMLDocument": [
        "xml"
      ]
    }
  }));
  
  
    
  // passed at runtime, configurable via nodejs module
  if (typeof polyfill !== 'object') polyfill = {type: polyfill || 'auto'};
  
  var
    // V0 polyfill entry
    REGISTER_ELEMENT = 'registerElement',
  
    // pseudo-random number used as expando/unique name on feature detection
    UID = window.Math.random() * 10e4 >> 0,
  
    // IE < 11 only + old WebKit for attributes + feature detection
    EXPANDO_UID = '__' + REGISTER_ELEMENT + UID,
  
    // shortcuts and costants
    ADD_EVENT_LISTENER = 'addEventListener',
    ATTACHED = 'attached',
    CALLBACK = 'Callback',
    DETACHED = 'detached',
    EXTENDS = 'extends',
  
    ATTRIBUTE_CHANGED_CALLBACK = 'attributeChanged' + CALLBACK,
    ATTACHED_CALLBACK = ATTACHED + CALLBACK,
    CONNECTED_CALLBACK = 'connected' + CALLBACK,
    DISCONNECTED_CALLBACK = 'disconnected' + CALLBACK,
    CREATED_CALLBACK = 'created' + CALLBACK,
    DETACHED_CALLBACK = DETACHED + CALLBACK,
  
    ADDITION = 'ADDITION',
    MODIFICATION = 'MODIFICATION',
    REMOVAL = 'REMOVAL',
  
    DOM_ATTR_MODIFIED = 'DOMAttrModified',
    DOM_CONTENT_LOADED = 'DOMContentLoaded',
    DOM_SUBTREE_MODIFIED = 'DOMSubtreeModified',
  
    PREFIX_TAG = '<',
    PREFIX_IS = '=',
  
    // valid and invalid node names
    validName = /^[A-Z][._A-Z0-9]*-[-._A-Z0-9]*$/,
    invalidNames = [
      'ANNOTATION-XML',
      'COLOR-PROFILE',
      'FONT-FACE',
      'FONT-FACE-SRC',
      'FONT-FACE-URI',
      'FONT-FACE-FORMAT',
      'FONT-FACE-NAME',
      'MISSING-GLYPH'
    ],
  
    // registered types and their prototypes
    types = [],
    protos = [],
  
    // to query subnodes
    query = '',
  
    // html shortcut used to feature detect
    documentElement = document.documentElement,
  
    // ES5 inline helpers || basic patches
    indexOf = types.indexOf || function (v) {
      for(var i = this.length; i-- && this[i] !== v;){}
      return i;
    },
  
    // other helpers / shortcuts
    OP = Object.prototype,
    hOP = OP.hasOwnProperty,
    iPO = OP.isPrototypeOf,
  
    defineProperty = Object.defineProperty,
    empty = [],
    gOPD = Object.getOwnPropertyDescriptor,
    gOPN = Object.getOwnPropertyNames,
    gPO = Object.getPrototypeOf,
    sPO = Object.setPrototypeOf,
  
    // jshint proto: true
    hasProto = !!Object.__proto__,
  
    // V1 helpers
    fixGetClass = false,
    DRECEV1 = '__dreCEv1',
    customElements = window.customElements,
    usableCustomElements = !/^force/.test(polyfill.type) && !!(
      customElements &&
      customElements.define &&
      customElements.get &&
      customElements.whenDefined
    ),
    Dict = Object.create || Object,
    Map = window.Map || function Map() {
      var K = [], V = [], i;
      return {
        get: function (k) {
          return V[indexOf.call(K, k)];
        },
        set: function (k, v) {
          i = indexOf.call(K, k);
          if (i < 0) V[K.push(k) - 1] = v;
          else V[i] = v;
        }
      };
    },
    Promise = window.Promise || function (fn) {
      var
        notify = [],
        done = false,
        p = {
          'catch': function () {
            return p;
          },
          'then': function (cb) {
            notify.push(cb);
            if (done) setTimeout(resolve, 1);
            return p;
          }
        }
      ;
      function resolve(value) {
        done = true;
        while (notify.length) notify.shift()(value);
      }
      fn(resolve);
      return p;
    },
    justCreated = false,
    constructors = Dict(null),
    waitingList = Dict(null),
    nodeNames = new Map(),
    secondArgument = function (is) {
      return is.toLowerCase();
    },
  
    // used to create unique instances
    create = Object.create || function Bridge(proto) {
      // silly broken polyfill probably ever used but short enough to work
      return proto ? ((Bridge.prototype = proto), new Bridge()) : this;
    },
  
    // will set the prototype if possible
    // or copy over all properties
    setPrototype = sPO || (
      hasProto ?
        function (o, p) {
          o.__proto__ = p;
          return o;
        } : (
      (gOPN && gOPD) ?
        (function(){
          function setProperties(o, p) {
            for (var
              key,
              names = gOPN(p),
              i = 0, length = names.length;
              i < length; i++
            ) {
              key = names[i];
              if (!hOP.call(o, key)) {
                defineProperty(o, key, gOPD(p, key));
              }
            }
          }
          return function (o, p) {
            do {
              setProperties(o, p);
            } while ((p = gPO(p)) && !iPO.call(p, o));
            return o;
          };
        }()) :
        function (o, p) {
          for (var key in p) {
            o[key] = p[key];
          }
          return o;
        }
    )),
  
    // DOM shortcuts and helpers, if any
  
    MutationObserver = window.MutationObserver ||
                       window.WebKitMutationObserver,
  
    HTMLAnchorElement = window.HTMLAnchorElement,
  
    HTMLElementPrototype = (
      window.HTMLElement ||
      window.Element ||
      window.Node
    ).prototype,
  
    IE8 = !iPO.call(HTMLElementPrototype, documentElement),
  
    safeProperty = IE8 ? function (o, k, d) {
      o[k] = d.value;
      return o;
    } : defineProperty,
  
    isValidNode = IE8 ?
      function (node) {
        return node.nodeType === 1;
      } :
      function (node) {
        return iPO.call(HTMLElementPrototype, node);
      },
  
    targets = IE8 && [],
  
    attachShadow = HTMLElementPrototype.attachShadow,
    cloneNode = HTMLElementPrototype.cloneNode,
    closest = HTMLElementPrototype.closest || function (name) {
      var self = this;
      while (self && self.nodeName !== name)
        self = self.parentNode;
      return self;
    },
    dispatchEvent = HTMLElementPrototype.dispatchEvent,
    getAttribute = HTMLElementPrototype.getAttribute,
    hasAttribute = HTMLElementPrototype.hasAttribute,
    removeAttribute = HTMLElementPrototype.removeAttribute,
    setAttribute = HTMLElementPrototype.setAttribute,
  
    // replaced later on
    createElement = document.createElement,
    importNode = document.importNode,
    patchedCreateElement = createElement,
  
    // shared observer for all attributes
    attributesObserver = MutationObserver && {
      attributes: true,
      characterData: true,
      attributeOldValue: true
    },
  
    // useful to detect only if there's no MutationObserver
    DOMAttrModified = MutationObserver || function(e) {
      doesNotSupportDOMAttrModified = false;
      documentElement.removeEventListener(
        DOM_ATTR_MODIFIED,
        DOMAttrModified
      );
    },
  
    // will both be used to make DOMNodeInserted asynchronous
    asapQueue,
    asapTimer = 0,
  
    // internal flags
    V0 = REGISTER_ELEMENT in document &&
         !/^force-all/.test(polyfill.type),
    setListener = true,
    justSetup = false,
    doesNotSupportDOMAttrModified = true,
    dropDomContentLoaded = true,
  
    // needed for the innerHTML helper
    notFromInnerHTMLHelper = true,
  
    // optionally defined later on
    onSubtreeModified,
    callDOMAttrModified,
    getAttributesMirror,
    observer,
    observe,
  
    // based on setting prototype capability
    // will check proto or the expando attribute
    // in order to setup the node once
    patchIfNotAlready,
    patch,
  
    // used for tests
    tmp
  ;
  
  // IE11 disconnectedCallback issue #
  // to be tested before any createElement patch
  if (MutationObserver) {
    // original fix:
    // https://github.com/javan/mutation-observer-inner-html-shim
    tmp = document.createElement('div');
    tmp.innerHTML = '<div><div></div></div>';
    new MutationObserver(function (mutations, observer) {
      if (
        mutations[0] &&
        mutations[0].type == 'childList' &&
        !mutations[0].removedNodes[0].childNodes.length
      ) {
        tmp = gOPD(HTMLElementPrototype, 'innerHTML');
        var set = tmp && tmp.set;
        if (set)
          defineProperty(HTMLElementPrototype, 'innerHTML', {
            set: function (value) {
              while (this.lastChild)
                this.removeChild(this.lastChild);
              set.call(this, value);
            }
          });
      }
      observer.disconnect();
      tmp = null;
    }).observe(tmp, {childList: true, subtree: true});
    tmp.innerHTML = "";
  }
  
  // only if needed
  if (!V0) {
  
    if (sPO || hasProto) {
        patchIfNotAlready = function (node, proto) {
          if (!iPO.call(proto, node)) {
            setupNode(node, proto);
          }
        };
        patch = setupNode;
    } else {
        patchIfNotAlready = function (node, proto) {
          if (!node[EXPANDO_UID]) {
            node[EXPANDO_UID] = Object(true);
            setupNode(node, proto);
          }
        };
        patch = patchIfNotAlready;
    }
  
    if (IE8) {
      doesNotSupportDOMAttrModified = false;
      (function (){
        var
          descriptor = gOPD(HTMLElementPrototype, ADD_EVENT_LISTENER),
          addEventListener = descriptor.value,
          patchedRemoveAttribute = function (name) {
            var e = new CustomEvent(DOM_ATTR_MODIFIED, {bubbles: true});
            e.attrName = name;
            e.prevValue = getAttribute.call(this, name);
            e.newValue = null;
            e[REMOVAL] = e.attrChange = 2;
            removeAttribute.call(this, name);
            dispatchEvent.call(this, e);
          },
          patchedSetAttribute = function (name, value) {
            var
              had = hasAttribute.call(this, name),
              old = had && getAttribute.call(this, name),
              e = new CustomEvent(DOM_ATTR_MODIFIED, {bubbles: true})
            ;
            setAttribute.call(this, name, value);
            e.attrName = name;
            e.prevValue = had ? old : null;
            e.newValue = value;
            if (had) {
              e[MODIFICATION] = e.attrChange = 1;
            } else {
              e[ADDITION] = e.attrChange = 0;
            }
            dispatchEvent.call(this, e);
          },
          onPropertyChange = function (e) {
            // jshint eqnull:true
            var
              node = e.currentTarget,
              superSecret = node[EXPANDO_UID],
              propertyName = e.propertyName,
              event
            ;
            if (superSecret.hasOwnProperty(propertyName)) {
              superSecret = superSecret[propertyName];
              event = new CustomEvent(DOM_ATTR_MODIFIED, {bubbles: true});
              event.attrName = superSecret.name;
              event.prevValue = superSecret.value || null;
              event.newValue = (superSecret.value = node[propertyName] || null);
              if (event.prevValue == null) {
                event[ADDITION] = event.attrChange = 0;
              } else {
                event[MODIFICATION] = event.attrChange = 1;
              }
              dispatchEvent.call(node, event);
            }
          }
        ;
        descriptor.value = function (type, handler, capture) {
          if (
            type === DOM_ATTR_MODIFIED &&
            this[ATTRIBUTE_CHANGED_CALLBACK] &&
            this.setAttribute !== patchedSetAttribute
          ) {
            this[EXPANDO_UID] = {
              className: {
                name: 'class',
                value: this.className
              }
            };
            this.setAttribute = patchedSetAttribute;
            this.removeAttribute = patchedRemoveAttribute;
            addEventListener.call(this, 'propertychange', onPropertyChange);
          }
          addEventListener.call(this, type, handler, capture);
        };
        defineProperty(HTMLElementPrototype, ADD_EVENT_LISTENER, descriptor);
      }());
    } else if (!MutationObserver) {
      documentElement[ADD_EVENT_LISTENER](DOM_ATTR_MODIFIED, DOMAttrModified);
      documentElement.setAttribute(EXPANDO_UID, 1);
      documentElement.removeAttribute(EXPANDO_UID);
      if (doesNotSupportDOMAttrModified) {
        onSubtreeModified = function (e) {
          var
            node = this,
            oldAttributes,
            newAttributes,
            key
          ;
          if (node === e.target) {
            oldAttributes = node[EXPANDO_UID];
            node[EXPANDO_UID] = (newAttributes = getAttributesMirror(node));
            for (key in newAttributes) {
              if (!(key in oldAttributes)) {
                // attribute was added
                return callDOMAttrModified(
                  0,
                  node,
                  key,
                  oldAttributes[key],
                  newAttributes[key],
                  ADDITION
                );
              } else if (newAttributes[key] !== oldAttributes[key]) {
                // attribute was changed
                return callDOMAttrModified(
                  1,
                  node,
                  key,
                  oldAttributes[key],
                  newAttributes[key],
                  MODIFICATION
                );
              }
            }
            // checking if it has been removed
            for (key in oldAttributes) {
              if (!(key in newAttributes)) {
                // attribute removed
                return callDOMAttrModified(
                  2,
                  node,
                  key,
                  oldAttributes[key],
                  newAttributes[key],
                  REMOVAL
                );
              }
            }
          }
        };
        callDOMAttrModified = function (
          attrChange,
          currentTarget,
          attrName,
          prevValue,
          newValue,
          action
        ) {
          var e = {
            attrChange: attrChange,
            currentTarget: currentTarget,
            attrName: attrName,
            prevValue: prevValue,
            newValue: newValue
          };
          e[action] = attrChange;
          onDOMAttrModified(e);
        };
        getAttributesMirror = function (node) {
          for (var
            attr, name,
            result = {},
            attributes = node.attributes,
            i = 0, length = attributes.length;
            i < length; i++
          ) {
            attr = attributes[i];
            name = attr.name;
            if (name !== 'setAttribute') {
              result[name] = attr.value;
            }
          }
          return result;
        };
      }
    }
  
    // set as enumerable, writable and configurable
    document[REGISTER_ELEMENT] = function registerElement(type, options) {
      upperType = type.toUpperCase();
      if (setListener) {
        // only first time document.registerElement is used
        // we need to set this listener
        // setting it by default might slow down for no reason
        setListener = false;
        if (MutationObserver) {
          observer = (function(attached, detached){
            function checkEmAll(list, callback) {
              for (var i = 0, length = list.length; i < length; callback(list[i++])){}
            }
            return new MutationObserver(function (records) {
              for (var
                current, node, newValue,
                i = 0, length = records.length; i < length; i++
              ) {
                current = records[i];
                if (current.type === 'childList') {
                  checkEmAll(current.addedNodes, attached);
                  checkEmAll(current.removedNodes, detached);
                } else {
                  node = current.target;
                  if (notFromInnerHTMLHelper &&
                      node[ATTRIBUTE_CHANGED_CALLBACK] &&
                      current.attributeName !== 'style') {
                    newValue = getAttribute.call(node, current.attributeName);
                    if (newValue !== current.oldValue) {
                      node[ATTRIBUTE_CHANGED_CALLBACK](
                        current.attributeName,
                        current.oldValue,
                        newValue
                      );
                    }
                  }
                }
              }
            });
          }(executeAction(ATTACHED), executeAction(DETACHED)));
          observe = function (node) {
            observer.observe(
              node,
              {
                childList: true,
                subtree: true
              }
            );
            return node;
          };
          observe(document);
          if (attachShadow) {
            HTMLElementPrototype.attachShadow = function () {
              return observe(attachShadow.apply(this, arguments));
            };
          }
        } else {
          asapQueue = [];
          document[ADD_EVENT_LISTENER]('DOMNodeInserted', onDOMNode(ATTACHED));
          document[ADD_EVENT_LISTENER]('DOMNodeRemoved', onDOMNode(DETACHED));
        }
  
        document[ADD_EVENT_LISTENER](DOM_CONTENT_LOADED, onReadyStateChange);
        document[ADD_EVENT_LISTENER]('readystatechange', onReadyStateChange);
  
        document.importNode = function (node, deep) {
          switch (node.nodeType) {
            case 1:
              return setupAll(document, importNode, [node, !!deep]);
            case 11:
              for (var
                fragment = document.createDocumentFragment(),
                childNodes = node.childNodes,
                length = childNodes.length,
                i = 0; i < length; i++
              )
                fragment.appendChild(document.importNode(childNodes[i], !!deep));
              return fragment;
            default:
              return cloneNode.call(node, !!deep);
          }
        };
  
        HTMLElementPrototype.cloneNode = function (deep) {
          return setupAll(this, cloneNode, [!!deep]);
        };
      }
  
      if (justSetup) return (justSetup = false);
  
      if (-2 < (
        indexOf.call(types, PREFIX_IS + upperType) +
        indexOf.call(types, PREFIX_TAG + upperType)
      )) {
        throwTypeError(type);
      }
  
      if (!validName.test(upperType) || -1 < indexOf.call(invalidNames, upperType)) {
        throw new Error('The type ' + type + ' is invalid');
      }
  
      var
        constructor = function () {
          return extending ?
            document.createElement(nodeName, upperType) :
            document.createElement(nodeName);
        },
        opt = options || OP,
        extending = hOP.call(opt, EXTENDS),
        nodeName = extending ? options[EXTENDS].toUpperCase() : upperType,
        upperType,
        i
      ;
  
      if (extending && -1 < (
        indexOf.call(types, PREFIX_TAG + nodeName)
      )) {
        throwTypeError(nodeName);
      }
  
      i = types.push((extending ? PREFIX_IS : PREFIX_TAG) + upperType) - 1;
  
      query = query.concat(
        query.length ? ',' : '',
        extending ? nodeName + '[is="' + type.toLowerCase() + '"]' : nodeName
      );
  
      constructor.prototype = (
        protos[i] = hOP.call(opt, 'prototype') ?
          opt.prototype :
          create(HTMLElementPrototype)
      );
  
      if (query.length) loopAndVerify(
        document.querySelectorAll(query),
        ATTACHED
      );
  
      return constructor;
    };
  
    document.createElement = (patchedCreateElement = function (localName, typeExtension) {
      var
        is = getIs(typeExtension),
        node = is ?
          createElement.call(document, localName, secondArgument(is)) :
          createElement.call(document, localName),
        name = '' + localName,
        i = indexOf.call(
          types,
          (is ? PREFIX_IS : PREFIX_TAG) +
          (is || name).toUpperCase()
        ),
        setup = -1 < i
      ;
      if (is) {
        node.setAttribute('is', is = is.toLowerCase());
        if (setup) {
          setup = isInQSA(name.toUpperCase(), is);
        }
      }
      notFromInnerHTMLHelper = !document.createElement.innerHTMLHelper;
      if (setup) patch(node, protos[i]);
      return node;
    });
  
  }
  
  // needed due unbelievable IE11 behavior
  // https://github.com/WebReflection/document-register-element/issues/175#issuecomment-520904688
  addEventListener(
    'beforeunload',
    function () {
      delete document.createElement;
      delete document.importNode;
      delete document[REGISTER_ELEMENT];
    },
    false
  );
  
  function ASAP() {
    var queue = asapQueue.splice(0, asapQueue.length);
    asapTimer = 0;
    while (queue.length) {
      queue.shift().call(
        null, queue.shift()
      );
    }
  }
  
  function loopAndVerify(list, action) {
    for (var i = 0, length = list.length; i < length; i++) {
      verifyAndSetupAndAction(list[i], action);
    }
  }
  
  function loopAndSetup(list) {
    for (var i = 0, length = list.length, node; i < length; i++) {
      node = list[i];
      patch(node, protos[getTypeIndex(node)]);
    }
  }
  
  function executeAction(action) {
    return function (node) {
      if (isValidNode(node)) {
        verifyAndSetupAndAction(node, action);
        if (query.length) loopAndVerify(
          node.querySelectorAll(query),
          action
        );
      }
    };
  }
  
  function getTypeIndex(target) {
    var
      is = getAttribute.call(target, 'is'),
      nodeName = target.nodeName.toUpperCase(),
      i = indexOf.call(
        types,
        is ?
            PREFIX_IS + is.toUpperCase() :
            PREFIX_TAG + nodeName
      )
    ;
    return is && -1 < i && !isInQSA(nodeName, is) ? -1 : i;
  }
  
  function isInQSA(name, type) {
    return -1 < query.indexOf(name + '[is="' + type + '"]');
  }
  
  function onDOMAttrModified(e) {
    var
      node = e.currentTarget,
      attrChange = e.attrChange,
      attrName = e.attrName,
      target = e.target,
      addition = e[ADDITION] || 2,
      removal = e[REMOVAL] || 3
    ;
    if (notFromInnerHTMLHelper &&
        (!target || target === node) &&
        node[ATTRIBUTE_CHANGED_CALLBACK] &&
        attrName !== 'style' && (
          e.prevValue !== e.newValue ||
          // IE9, IE10, and Opera 12 gotcha
          e.newValue === '' && (
            attrChange === addition ||
            attrChange === removal
          )
    )) {
      node[ATTRIBUTE_CHANGED_CALLBACK](
        attrName,
        attrChange === addition ? null : e.prevValue,
        attrChange === removal ? null : e.newValue
      );
    }
  }
  
  function onDOMNode(action) {
    var executor = executeAction(action);
    return function (e) {
      asapQueue.push(executor, e.target);
      if (asapTimer) clearTimeout(asapTimer);
      asapTimer = setTimeout(ASAP, 1);
    };
  }
  
  function onReadyStateChange(e) {
    if (dropDomContentLoaded) {
      dropDomContentLoaded = false;
      e.currentTarget.removeEventListener(DOM_CONTENT_LOADED, onReadyStateChange);
    }
    if (query.length) loopAndVerify(
      (e.target || document).querySelectorAll(query),
      e.detail === DETACHED ? DETACHED : ATTACHED
    );
    if (IE8) purge();
  }
  
  function patchedSetAttribute(name, value) {
    // jshint validthis:true
    var self = this;
    setAttribute.call(self, name, value);
    onSubtreeModified.call(self, {target: self});
  }
  
  function setupAll(context, callback, args) {
    var
      node = callback.apply(context, args),
      i = getTypeIndex(node)
    ;
    if (-1 < i) patch(node, protos[i]);
    if (args.pop() && query.length)
      loopAndSetup(node.querySelectorAll(query));
    return node;
  }
  
  function setupNode(node, proto) {
    setPrototype(node, proto);
    if (observer) {
      observer.observe(node, attributesObserver);
    } else {
      if (doesNotSupportDOMAttrModified) {
        node.setAttribute = patchedSetAttribute;
        node[EXPANDO_UID] = getAttributesMirror(node);
        node[ADD_EVENT_LISTENER](DOM_SUBTREE_MODIFIED, onSubtreeModified);
      }
      node[ADD_EVENT_LISTENER](DOM_ATTR_MODIFIED, onDOMAttrModified);
    }
    if (node[CREATED_CALLBACK] && notFromInnerHTMLHelper) {
      node.created = true;
      node[CREATED_CALLBACK]();
      node.created = false;
    }
  }
  
  function purge() {
    for (var
      node,
      i = 0,
      length = targets.length;
      i < length; i++
    ) {
      node = targets[i];
      if (!documentElement.contains(node)) {
        length--;
        targets.splice(i--, 1);
        verifyAndSetupAndAction(node, DETACHED);
      }
    }
  }
  
  function throwTypeError(type) {
    throw new Error('A ' + type + ' type is already registered');
  }
  
  function verifyAndSetupAndAction(node, action) {
    var
      fn,
      i = getTypeIndex(node),
      counterAction
    ;
    if ((-1 < i) && !closest.call(node, 'TEMPLATE')) {
      patchIfNotAlready(node, protos[i]);
      i = 0;
      if (action === ATTACHED && !node[ATTACHED]) {
        node[DETACHED] = false;
        node[ATTACHED] = true;
        counterAction = 'connected';
        i = 1;
        if (IE8 && indexOf.call(targets, node) < 0) {
          targets.push(node);
        }
      } else if (action === DETACHED && !node[DETACHED]) {
        node[ATTACHED] = false;
        node[DETACHED] = true;
        counterAction = 'disconnected';
        i = 1;
      }
      if (i && (fn = (
        node[action + CALLBACK] ||
        node[counterAction + CALLBACK]
      ))) fn.call(node);
    }
  }
  
  // V1 in da House!
  function CustomElementRegistry() {}
  
  CustomElementRegistry.prototype = {
    constructor: CustomElementRegistry,
    // a workaround for the stubborn WebKit
    define: usableCustomElements ?
      function (name, Class, options) {
        if (options) {
          CERDefine(name, Class, options);
        } else {
          var NAME = name.toUpperCase();
          constructors[NAME] = {
            constructor: Class,
            create: [NAME]
          };
          nodeNames.set(Class, NAME);
          customElements.define(name, Class);
        }
      } :
      CERDefine,
    get: usableCustomElements ?
      function (name) {
        return customElements.get(name) || get(name);
      } :
      get,
    whenDefined: usableCustomElements ?
      function (name) {
        return Promise.race([
          customElements.whenDefined(name),
          whenDefined(name)
        ]);
      } :
      whenDefined
  };
  
  function CERDefine(name, Class, options) {
    var
      is = options && options[EXTENDS] || '',
      CProto = Class.prototype,
      proto = create(CProto),
      attributes = Class.observedAttributes || empty,
      definition = {prototype: proto}
    ;
    // TODO: is this needed at all since it's inherited?
    // defineProperty(proto, 'constructor', {value: Class});
    safeProperty(proto, CREATED_CALLBACK, {
        value: function () {
          if (justCreated) justCreated = false;
          else if (!this[DRECEV1]) {
            this[DRECEV1] = true;
            new Class(this);
            if (CProto[CREATED_CALLBACK])
              CProto[CREATED_CALLBACK].call(this);
            var info = constructors[nodeNames.get(Class)];
            if (!usableCustomElements || info.create.length > 1) {
              notifyAttributes(this);
            }
          }
      }
    });
    safeProperty(proto, ATTRIBUTE_CHANGED_CALLBACK, {
      value: function (name) {
        if (-1 < indexOf.call(attributes, name)) {
          if (CProto[ATTRIBUTE_CHANGED_CALLBACK])
            CProto[ATTRIBUTE_CHANGED_CALLBACK].apply(this, arguments);
        }
      }
    });
    if (CProto[CONNECTED_CALLBACK]) {
      safeProperty(proto, ATTACHED_CALLBACK, {
        value: CProto[CONNECTED_CALLBACK]
      });
    }
    if (CProto[DISCONNECTED_CALLBACK]) {
      safeProperty(proto, DETACHED_CALLBACK, {
        value: CProto[DISCONNECTED_CALLBACK]
      });
    }
    if (is) definition[EXTENDS] = is;
    name = name.toUpperCase();
    constructors[name] = {
      constructor: Class,
      create: is ? [is, secondArgument(name)] : [name]
    };
    nodeNames.set(Class, name);
    document[REGISTER_ELEMENT](name.toLowerCase(), definition);
    whenDefined(name);
    waitingList[name].r();
  }
  
  function get(name) {
    var info = constructors[name.toUpperCase()];
    return info && info.constructor;
  }
  
  function getIs(options) {
    return typeof options === 'string' ?
        options : (options && options.is || '');
  }
  
  function notifyAttributes(self) {
    var
      callback = self[ATTRIBUTE_CHANGED_CALLBACK],
      attributes = callback ? self.attributes : empty,
      i = attributes.length,
      attribute
    ;
    while (i--) {
      attribute =  attributes[i]; // || attributes.item(i);
      callback.call(
        self,
        attribute.name || attribute.nodeName,
        null,
        attribute.value || attribute.nodeValue
      );
    }
  }
  
  function whenDefined(name) {
    name = name.toUpperCase();
    if (!(name in waitingList)) {
      waitingList[name] = {};
      waitingList[name].p = new Promise(function (resolve) {
        waitingList[name].r = resolve;
      });
    }
    return waitingList[name].p;
  }
  
  function polyfillV1() {
    if (customElements) delete window.customElements;
    defineProperty(window, 'customElements', {
      configurable: true,
      value: new CustomElementRegistry()
    });
    defineProperty(window, 'CustomElementRegistry', {
      configurable: true,
      value: CustomElementRegistry
    });
    for (var
      patchClass = function (name) {
        var Class = window[name];
        if (Class) {
          window[name] = function CustomElementsV1(self) {
            var info, isNative;
            if (!self) self = this;
            if (!self[DRECEV1]) {
              justCreated = true;
              info = constructors[nodeNames.get(self.constructor)];
              isNative = usableCustomElements && info.create.length === 1;
              self = isNative ?
                Reflect.construct(Class, empty, info.constructor) :
                document.createElement.apply(document, info.create);
              self[DRECEV1] = true;
              justCreated = false;
              if (!isNative) notifyAttributes(self);
            }
            return self;
          };
          window[name].prototype = Class.prototype;
          try {
            Class.prototype.constructor = window[name];
          } catch(WebKit) {
            fixGetClass = true;
            defineProperty(Class, DRECEV1, {value: window[name]});
          }
        }
      },
      Classes = htmlClass.get(/^HTML[A-Z]*[a-z]/),
      i = Classes.length;
      i--;
      patchClass(Classes[i])
    ) {}
    (document.createElement = function (name, options) {
      var is = getIs(options);
      return is ?
        patchedCreateElement.call(this, name, secondArgument(is)) :
        patchedCreateElement.call(this, name);
    });
    if (!V0) {
      justSetup = true;
      document[REGISTER_ELEMENT]('');
    }
  }
  
  // if customElements is not there at all
  if (!customElements || /^force/.test(polyfill.type)) polyfillV1();
  else if(!polyfill.noBuiltIn) {
    // if available test extends work as expected
    try {
      (function (DRE, options, name) {
        var re = new RegExp('^<a\\s+is=(\'|")' + name + '\\1></a>$');
        options[EXTENDS] = 'a';
        DRE.prototype = create(HTMLAnchorElement.prototype);
        DRE.prototype.constructor = DRE;
        window.customElements.define(name, DRE, options);
        if (
          !re.test(document.createElement('a', {is: name}).outerHTML) ||
          !re.test((new DRE()).outerHTML)
        ) {
          throw options;
        }
      }(
        function DRE() {
          return Reflect.construct(HTMLAnchorElement, [], DRE);
        },
        {},
        'document-register-element-a' + UID
      ));
    } catch(o_O) {
      // or force the polyfill if not
      // and keep internal original reference
      polyfillV1();
    }
  }
  
  // FireFox only issue
  if(!polyfill.noBuiltIn) {
    try {
      if (createElement.call(document, 'a', 'a').outerHTML.indexOf('is') < 0)
        throw {};
    } catch(FireFox) {
      secondArgument = function (is) {
        return {is: is.toLowerCase()};
      };
    }
  }
  
}

module.exports = installCustomElements;

},{}],22:[function(require,module,exports){
'use strict';
/*! (c) Andrea Giammarchi - ISC */

// Custom
var UID = '-' + Math.random().toFixed(6) + '%';
//                           Edge issue!

var UID_IE = false;

try {
  if (!(function (template, content, tabindex) {
    return content in template && (
      (template.innerHTML = '<p ' + tabindex + '="' + UID + '"></p>'),
      template[content].childNodes[0].getAttribute(tabindex) == UID
    );
  }(document.createElement('template'), 'content', 'tabindex'))) {
    UID = '_dt: ' + UID.slice(1, -1) + ';';
    UID_IE = true;
  }
} catch(meh) {}

var UIDC = '<!--' + UID + '-->';

// DOM
var COMMENT_NODE = 8;
var DOCUMENT_FRAGMENT_NODE = 11;
var ELEMENT_NODE = 1;
var TEXT_NODE = 3;

var SHOULD_USE_TEXT_CONTENT = /^(?:style|textarea)$/i;
var VOID_ELEMENTS = /^(?:area|base|br|col|embed|hr|img|input|keygen|link|menuitem|meta|param|source|track|wbr)$/i;

exports.UID = UID;
exports.UIDC = UIDC;
exports.UID_IE = UID_IE;
exports.COMMENT_NODE = COMMENT_NODE;
exports.DOCUMENT_FRAGMENT_NODE = DOCUMENT_FRAGMENT_NODE;
exports.ELEMENT_NODE = ELEMENT_NODE;
exports.TEXT_NODE = TEXT_NODE;
exports.SHOULD_USE_TEXT_CONTENT = SHOULD_USE_TEXT_CONTENT;
exports.VOID_ELEMENTS = VOID_ELEMENTS;

},{}],23:[function(require,module,exports){
'use strict';
/*! (c) 2018 Andrea Giammarchi (ISC) */

const {
  eqeq, identity, indexOf, isReversed, next, append, remove, smartDiff
} = require('./utils.js');

const domdiff = (
  parentNode,     // where changes happen
  currentNodes,   // Array of current items/nodes
  futureNodes,    // Array of future items/nodes
  options         // optional object with one of the following properties
                  //  before: domNode
                  //  compare(generic, generic) => true if same generic
                  //  node(generic) => Node
) => {
  if (!options)
    options = {};

  const compare = options.compare || eqeq;
  const get = options.node || identity;
  const before = options.before == null ? null : get(options.before, 0);

  const currentLength = currentNodes.length;
  let currentEnd = currentLength;
  let currentStart = 0;

  let futureEnd = futureNodes.length;
  let futureStart = 0;

  // common prefix
  while (
    currentStart < currentEnd &&
    futureStart < futureEnd &&
    compare(currentNodes[currentStart], futureNodes[futureStart])
  ) {
    currentStart++;
    futureStart++;
  }

  // common suffix
  while (
    currentStart < currentEnd &&
    futureStart < futureEnd &&
    compare(currentNodes[currentEnd - 1], futureNodes[futureEnd - 1])
  ) {
    currentEnd--;
    futureEnd--;
  }

  const currentSame = currentStart === currentEnd;
  const futureSame = futureStart === futureEnd;

  // same list
  if (currentSame && futureSame)
    return futureNodes;

  // only stuff to add
  if (currentSame && futureStart < futureEnd) {
    append(
      get,
      parentNode,
      futureNodes,
      futureStart,
      futureEnd,
      next(get, currentNodes, currentStart, currentLength, before)
    );
    return futureNodes;
  }

  // only stuff to remove
  if (futureSame && currentStart < currentEnd) {
    remove(
      get,
      currentNodes,
      currentStart,
      currentEnd
    );
    return futureNodes;
  }

  const currentChanges = currentEnd - currentStart;
  const futureChanges = futureEnd - futureStart;
  let i = -1;

  // 2 simple indels: the shortest sequence is a subsequence of the longest
  if (currentChanges < futureChanges) {
    i = indexOf(
      futureNodes,
      futureStart,
      futureEnd,
      currentNodes,
      currentStart,
      currentEnd,
      compare
    );
    // inner diff
    if (-1 < i) {
      append(
        get,
        parentNode,
        futureNodes,
        futureStart,
        i,
        get(currentNodes[currentStart], 0)
      );
      append(
        get,
        parentNode,
        futureNodes,
        i + currentChanges,
        futureEnd,
        next(get, currentNodes, currentEnd, currentLength, before)
      );
      return futureNodes;
    }
  }
  /* istanbul ignore else */
  else if (futureChanges < currentChanges) {
    i = indexOf(
      currentNodes,
      currentStart,
      currentEnd,
      futureNodes,
      futureStart,
      futureEnd,
      compare
    );
    // outer diff
    if (-1 < i) {
      remove(
        get,
        currentNodes,
        currentStart,
        i
      );
      remove(
        get,
        currentNodes,
        i + futureChanges,
        currentEnd
      );
      return futureNodes;
    }
  }

  // common case with one replacement for many nodes
  // or many nodes replaced for a single one
  /* istanbul ignore else */
  if ((currentChanges < 2 || futureChanges < 2)) {
    append(
      get,
      parentNode,
      futureNodes,
      futureStart,
      futureEnd,
      get(currentNodes[currentStart], 0)
    );
    remove(
      get,
      currentNodes,
      currentStart,
      currentEnd
    );
    return futureNodes;
  }

  // the half match diff part has been skipped in petit-dom
  // https://github.com/yelouafi/petit-dom/blob/bd6f5c919b5ae5297be01612c524c40be45f14a7/src/vdom.js#L391-L397
  // accordingly, I think it's safe to skip in here too
  // if one day it'll come out like the speediest thing ever to do
  // then I might add it in here too

  // Extra: before going too fancy, what about reversed lists ?
  //        This should bail out pretty quickly if that's not the case.
  if (
    currentChanges === futureChanges &&
    isReversed(
      futureNodes,
      futureEnd,
      currentNodes,
      currentStart,
      currentEnd,
      compare
    )
  ) {
    append(
      get,
      parentNode,
      futureNodes,
      futureStart,
      futureEnd,
      next(get, currentNodes, currentEnd, currentLength, before)
    );
    return futureNodes;
  }

  // last resort through a smart diff
  smartDiff(
    get,
    parentNode,
    futureNodes,
    futureStart,
    futureEnd,
    futureChanges,
    currentNodes,
    currentStart,
    currentEnd,
    currentChanges,
    currentLength,
    compare,
    before
  );

  return futureNodes;
};

Object.defineProperty(exports, '__esModule', {value: true}).default = domdiff;

},{"./utils.js":24}],24:[function(require,module,exports){
'use strict';
const {indexOf: iOF} = require('uarray');

const append = (get, parent, children, start, end, before) => {
  const isSelect = 'selectedIndex' in parent;
  let noSelection = isSelect;
  while (start < end) {
    const child = get(children[start], 1);
    parent.insertBefore(child, before);
    if (isSelect && noSelection && child.selected) {
      noSelection = !noSelection;
      let {selectedIndex} = parent;
      parent.selectedIndex = selectedIndex < 0 ?
        start :
        iOF.call(parent.querySelectorAll('option'), child);
    }
    start++;
  }
};
exports.append = append;

const eqeq = (a, b) => a == b;
exports.eqeq = eqeq;

const identity = O => O;
exports.identity = identity;

const indexOf = (
  moreNodes,
  moreStart,
  moreEnd,
  lessNodes,
  lessStart,
  lessEnd,
  compare
) => {
  const length = lessEnd - lessStart;
  /* istanbul ignore if */
  if (length < 1)
    return -1;
  while ((moreEnd - moreStart) >= length) {
    let m = moreStart;
    let l = lessStart;
    while (
      m < moreEnd &&
      l < lessEnd &&
      compare(moreNodes[m], lessNodes[l])
    ) {
      m++;
      l++;
    }
    if (l === lessEnd)
      return moreStart;
    moreStart = m + 1;
  }
  return -1;
};
exports.indexOf = indexOf;

const isReversed = (
  futureNodes,
  futureEnd,
  currentNodes,
  currentStart,
  currentEnd,
  compare
) => {
  while (
    currentStart < currentEnd &&
    compare(
      currentNodes[currentStart],
      futureNodes[futureEnd - 1]
    )) {
      currentStart++;
      futureEnd--;
    };
  return futureEnd === 0;
};
exports.isReversed = isReversed;

const next = (get, list, i, length, before) => i < length ?
              get(list[i], 0) :
              (0 < i ?
                get(list[i - 1], -0).nextSibling :
                before);
exports.next = next;

const remove = (get, children, start, end) => {
  while (start < end)
    drop(get(children[start++], -1));
};
exports.remove = remove;

// - - - - - - - - - - - - - - - - - - -
// diff related constants and utilities
// - - - - - - - - - - - - - - - - - - -

const DELETION = -1;
const INSERTION = 1;
const SKIP = 0;
const SKIP_OND = 50;

const HS = (
  futureNodes,
  futureStart,
  futureEnd,
  futureChanges,
  currentNodes,
  currentStart,
  currentEnd,
  currentChanges
) => {

  let k = 0;
  /* istanbul ignore next */
  let minLen = futureChanges < currentChanges ? futureChanges : currentChanges;
  const link = Array(minLen++);
  const tresh = Array(minLen);
  tresh[0] = -1;

  for (let i = 1; i < minLen; i++)
    tresh[i] = currentEnd;

  const nodes = currentNodes.slice(currentStart, currentEnd);

  for (let i = futureStart; i < futureEnd; i++) {
    const index = nodes.indexOf(futureNodes[i]);
    if (-1 < index) {
      const idxInOld = index + currentStart;
      k = findK(tresh, minLen, idxInOld);
      /* istanbul ignore else */
      if (-1 < k) {
        tresh[k] = idxInOld;
        link[k] = {
          newi: i,
          oldi: idxInOld,
          prev: link[k - 1]
        };
      }
    }
  }

  k = --minLen;
  --currentEnd;
  while (tresh[k] > currentEnd) --k;

  minLen = currentChanges + futureChanges - k;
  const diff = Array(minLen);
  let ptr = link[k];
  --futureEnd;
  while (ptr) {
    const {newi, oldi} = ptr;
    while (futureEnd > newi) {
      diff[--minLen] = INSERTION;
      --futureEnd;
    }
    while (currentEnd > oldi) {
      diff[--minLen] = DELETION;
      --currentEnd;
    }
    diff[--minLen] = SKIP;
    --futureEnd;
    --currentEnd;
    ptr = ptr.prev;
  }
  while (futureEnd >= futureStart) {
    diff[--minLen] = INSERTION;
    --futureEnd;
  }
  while (currentEnd >= currentStart) {
    diff[--minLen] = DELETION;
    --currentEnd;
  }
  return diff;
};

// this is pretty much the same petit-dom code without the delete map part
// https://github.com/yelouafi/petit-dom/blob/bd6f5c919b5ae5297be01612c524c40be45f14a7/src/vdom.js#L556-L561
const OND = (
  futureNodes,
  futureStart,
  rows,
  currentNodes,
  currentStart,
  cols,
  compare
) => {
  const length = rows + cols;
  const v = [];
  let d, k, r, c, pv, cv, pd;
  outer: for (d = 0; d <= length; d++) {
    /* istanbul ignore if */
    if (d > SKIP_OND)
      return null;
    pd = d - 1;
    /* istanbul ignore next */
    pv = d ? v[d - 1] : [0, 0];
    cv = v[d] = [];
    for (k = -d; k <= d; k += 2) {
      if (k === -d || (k !== d && pv[pd + k - 1] < pv[pd + k + 1])) {
        c = pv[pd + k + 1];
      } else {
        c = pv[pd + k - 1] + 1;
      }
      r = c - k;
      while (
        c < cols &&
        r < rows &&
        compare(
          currentNodes[currentStart + c],
          futureNodes[futureStart + r]
        )
      ) {
        c++;
        r++;
      }
      if (c === cols && r === rows) {
        break outer;
      }
      cv[d + k] = c;
    }
  }

  const diff = Array(d / 2 + length / 2);
  let diffIdx = diff.length - 1;
  for (d = v.length - 1; d >= 0; d--) {
    while (
      c > 0 &&
      r > 0 &&
      compare(
        currentNodes[currentStart + c - 1],
        futureNodes[futureStart + r - 1]
      )
    ) {
      // diagonal edge = equality
      diff[diffIdx--] = SKIP;
      c--;
      r--;
    }
    if (!d)
      break;
    pd = d - 1;
    /* istanbul ignore next */
    pv = d ? v[d - 1] : [0, 0];
    k = c - r;
    if (k === -d || (k !== d && pv[pd + k - 1] < pv[pd + k + 1])) {
      // vertical edge = insertion
      r--;
      diff[diffIdx--] = INSERTION;
    } else {
      // horizontal edge = deletion
      c--;
      diff[diffIdx--] = DELETION;
    }
  }
  return diff;
};

const applyDiff = (
  diff,
  get,
  parentNode,
  futureNodes,
  futureStart,
  currentNodes,
  currentStart,
  currentLength,
  before
) => {
  const live = [];
  const length = diff.length;
  let currentIndex = currentStart;
  let i = 0;
  while (i < length) {
    switch (diff[i++]) {
      case SKIP:
        futureStart++;
        currentIndex++;
        break;
      case INSERTION:
        // TODO: bulk appends for sequential nodes
        live.push(futureNodes[futureStart]);
        append(
          get,
          parentNode,
          futureNodes,
          futureStart++,
          futureStart,
          currentIndex < currentLength ?
            get(currentNodes[currentIndex], 0) :
            before
        );
        break;
      case DELETION:
        currentIndex++;
        break;
    }
  }
  i = 0;
  while (i < length) {
    switch (diff[i++]) {
      case SKIP:
        currentStart++;
        break;
      case DELETION:
        // TODO: bulk removes for sequential nodes
        if (-1 < live.indexOf(currentNodes[currentStart]))
          currentStart++;
        else
          remove(
            get,
            currentNodes,
            currentStart++,
            currentStart
          );
        break;
    }
  }
};

const findK = (ktr, length, j) => {
  let lo = 1;
  let hi = length;
  while (lo < hi) {
    const mid = ((lo + hi) / 2) >>> 0;
    if (j < ktr[mid])
      hi = mid;
    else
      lo = mid + 1;
  }
  return lo;
}

const smartDiff = (
  get,
  parentNode,
  futureNodes,
  futureStart,
  futureEnd,
  futureChanges,
  currentNodes,
  currentStart,
  currentEnd,
  currentChanges,
  currentLength,
  compare,
  before
) => {
  applyDiff(
    OND(
      futureNodes,
      futureStart,
      futureChanges,
      currentNodes,
      currentStart,
      currentChanges,
      compare
    ) ||
    HS(
      futureNodes,
      futureStart,
      futureEnd,
      futureChanges,
      currentNodes,
      currentStart,
      currentEnd,
      currentChanges
    ),
    get,
    parentNode,
    futureNodes,
    futureStart,
    currentNodes,
    currentStart,
    currentLength,
    before
  );
};
exports.smartDiff = smartDiff;

const drop = node => (node.remove || dropChild).call(node);

function dropChild() {
  const {parentNode} = this;
  /* istanbul ignore else */
  if (parentNode)
    parentNode.removeChild(this);
}

},{"uarray":38}],25:[function(require,module,exports){
'use strict';
/*! (c) Andrea Giammarchi - ISC */

const {UID, UIDC, VOID_ELEMENTS} = require('domconstants');

Object.defineProperty(exports, '__esModule', {value: true}).default = function (template) {
  return template.join(UIDC)
          .replace(selfClosing, fullClosing)
          .replace(attrSeeker, attrReplacer);
}

var spaces = ' \\f\\n\\r\\t';
var almostEverything = '[^' + spaces + '\\/>"\'=]+';
var attrName = '[' + spaces + ']+' + almostEverything;
var tagName = '<([A-Za-z]+[A-Za-z0-9:._-]*)((?:';
var attrPartials = '(?:\\s*=\\s*(?:\'[^\']*?\'|"[^"]*?"|<[^>]*?>|' + almostEverything.replace('\\/', '') + '))?)';

var attrSeeker = new RegExp(tagName + attrName + attrPartials + '+)([' + spaces + ']*/?>)', 'g');
var selfClosing = new RegExp(tagName + attrName + attrPartials + '*)([' + spaces + ']*/>)', 'g');
var findAttributes = new RegExp('(' + attrName + '\\s*=\\s*)([\'"]?)' + UIDC + '\\2', 'gi');

function attrReplacer($0, $1, $2, $3) {
  return '<' + $1 + $2.replace(findAttributes, replaceAttributes) + $3;
}

function replaceAttributes($0, $1, $2) {
  return $1 + ($2 || '"') + UID + ($2 || '"');
}

function fullClosing($0, $1, $2) {
  return VOID_ELEMENTS.test($1) ? $0 : ('<' + $1 + $2 + '></' + $1 + '>');
}

},{"domconstants":22}],26:[function(require,module,exports){
'use strict';
// globals
const WeakMap = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('@ungap/weakmap'));

// utils
const createContent = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('@ungap/create-content'));
const importNode = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('@ungap/import-node'));
const trim = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('@ungap/trim'));
const sanitize = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('domsanitizer'));
const umap = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('umap'));

// local
const {find, parse} = require('./walker.js');

// the domtagger 🎉
Object.defineProperty(exports, '__esModule', {value: true}).default = domtagger;

var parsed = umap(new WeakMap);

function createInfo(options, template) {
  var markup = (options.convert || sanitize)(template);
  var transform = options.transform;
  if (transform)
    markup = transform(markup);
  var content = createContent(markup, options.type);
  cleanContent(content);
  var holes = [];
  parse(content, holes, template.slice(0), []);
  return {
    content: content,
    updates: function (content) {
      var updates = [];
      var len = holes.length;
      var i = 0;
      var off = 0;
      while (i < len) {
        var info = holes[i++];
        var node = find(content, info.path);
        switch (info.type) {
          case 'any':
            updates.push({fn: options.any(node, []), sparse: false});
            break;
          case 'attr':
            var sparse = info.sparse;
            var fn = options.attribute(node, info.name, info.node);
            if (sparse === null)
              updates.push({fn: fn, sparse: false});
            else {
              off += sparse.length - 2;
              updates.push({fn: fn, sparse: true, values: sparse});
            }
            break;
          case 'text':
            updates.push({fn: options.text(node), sparse: false});
            node.textContent = '';
            break;
        }
      }
      len += off;
      return function () {
        var length = arguments.length;
        if (len !== (length - 1)) {
          throw new Error(
            (length - 1) + ' values instead of ' + len + '\n' +
            template.join('${value}')
          );
        }
        var i = 1;
        var off = 1;
        while (i < length) {
          var update = updates[i - off];
          if (update.sparse) {
            var values = update.values;
            var value = values[0];
            var j = 1;
            var l = values.length;
            off += l - 2;
            while (j < l)
              value += arguments[i++] + values[j++];
            update.fn(value);
          }
          else
            update.fn(arguments[i++]);
        }
        return content;
      };
    }
  };
}

function createDetails(options, template) {
  var info = parsed.get(template) || parsed.set(template, createInfo(options, template));
  return info.updates(importNode.call(document, info.content, true));
}

var empty = [];
function domtagger(options) {
  var previous = empty;
  var updates = cleanContent;
  return function (template) {
    if (previous !== template)
      updates = createDetails(options, (previous = template));
    return updates.apply(null, arguments);
  };
}

function cleanContent(fragment) {
  var childNodes = fragment.childNodes;
  var i = childNodes.length;
  while (i--) {
    var child = childNodes[i];
    if (
      child.nodeType !== 1 &&
      trim.call(child.textContent).length === 0
    ) {
      fragment.removeChild(child);
    }
  }
}

},{"./walker.js":27,"@ungap/create-content":10,"@ungap/import-node":14,"@ungap/trim":18,"@ungap/weakmap":19,"domsanitizer":25,"umap":39}],27:[function(require,module,exports){
'use strict';
const trim = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('@ungap/trim'));

const {
  UID, UIDC, UID_IE, COMMENT_NODE, ELEMENT_NODE, SHOULD_USE_TEXT_CONTENT, TEXT_NODE
} = require('domconstants');

exports.find = find;
exports.parse = parse;

/* istanbul ignore next */
var normalizeAttributes = UID_IE ?
  function (attributes, parts) {
    var html = parts.join(' ');
    return parts.slice.call(attributes, 0).sort(function (left, right) {
      return html.indexOf(left.name) <= html.indexOf(right.name) ? -1 : 1;
    });
  } :
  function (attributes, parts) {
    return parts.slice.call(attributes, 0);
  }
;

function find(node, path) {
  var length = path.length;
  var i = 0;
  while (i < length)
    node = node.childNodes[path[i++]];
  return node;
}

function parse(node, holes, parts, path) {
  var childNodes = node.childNodes;
  var length = childNodes.length;
  var i = 0;
  while (i < length) {
    var child = childNodes[i];
    switch (child.nodeType) {
      case ELEMENT_NODE:
        var childPath = path.concat(i);
        parseAttributes(child, holes, parts, childPath);
        parse(child, holes, parts, childPath);
        break;
      case COMMENT_NODE:
        var textContent = child.textContent;
        if (textContent === UID) {
          parts.shift();
          holes.push(
            // basicHTML or other non standard engines
            // might end up having comments in nodes
            // where they shouldn't, hence this check.
            SHOULD_USE_TEXT_CONTENT.test(node.nodeName) ?
              Text(node, path) :
              Any(child, path.concat(i))
          );
        } else {
          switch (textContent.slice(0, 2)) {
            case '/*':
              if (textContent.slice(-2) !== '*/')
                break;
            case '\uD83D\uDC7B': // ghost
              node.removeChild(child);
              i--;
              length--;
          }
        }
        break;
      case TEXT_NODE:
        // the following ignore is actually covered by browsers
        // only basicHTML ends up on previous COMMENT_NODE case
        // instead of TEXT_NODE because it knows nothing about
        // special style or textarea behavior
        /* istanbul ignore if */
        if (
          SHOULD_USE_TEXT_CONTENT.test(node.nodeName) &&
          trim.call(child.textContent) === UIDC
        ) {
          parts.shift();
          holes.push(Text(node, path));
        }
        break;
    }
    i++;
  }
}

function parseAttributes(node, holes, parts, path) {
  var attributes = node.attributes;
  var cache = [];
  var remove = [];
  var array = normalizeAttributes(attributes, parts);
  var length = array.length;
  var i = 0;
  while (i < length) {
    var attribute = array[i++];
    var direct = attribute.value === UID;
    var sparse;
    if (direct || 1 < (sparse = attribute.value.split(UIDC)).length) {
      var name = attribute.name;
      // the following ignore is covered by IE
      // and the IE9 double viewBox test
      /* istanbul ignore else */
      if (cache.indexOf(name) < 0) {
        cache.push(name);
        var realName = parts.shift().replace(
          direct ?
            /^(?:|[\S\s]*?\s)(\S+?)\s*=\s*('|")?$/ :
            new RegExp(
              '^(?:|[\\S\\s]*?\\s)(' + name + ')\\s*=\\s*(\'|")[\\S\\s]*',
              'i'
            ),
            '$1'
        );
        var value = attributes[realName] ||
                      // the following ignore is covered by browsers
                      // while basicHTML is already case-sensitive
                      /* istanbul ignore next */
                      attributes[realName.toLowerCase()];
        if (direct)
          holes.push(Attr(value, path, realName, null));
        else {
          var skip = sparse.length - 2;
          while (skip--)
            parts.shift();
          holes.push(Attr(value, path, realName, sparse));
        }
      }
      remove.push(attribute);
    }
  }
  length = remove.length;
  i = 0;

  /* istanbul ignore next */
  var cleanValue = 0 < length && UID_IE && !('ownerSVGElement' in node);
  while (i < length) {
    // Edge HTML bug #16878726
    var attr = remove[i++];
    // IE/Edge bug lighterhtml#63 - clean the value or it'll persist
    /* istanbul ignore next */
    if (cleanValue)
      attr.value = '';
    // IE/Edge bug lighterhtml#64 - don't use removeAttributeNode
    node.removeAttribute(attr.name);
  }

  // This is a very specific Firefox/Safari issue
  // but since it should be a not so common pattern,
  // it's probably worth patching regardless.
  // Basically, scripts created through strings are death.
  // You need to create fresh new scripts instead.
  // TODO: is there any other node that needs such nonsense?
  var nodeName = node.nodeName;
  if (/^script$/i.test(nodeName)) {
    // this used to be like that
    // var script = createElement(node, nodeName);
    // then Edge arrived and decided that scripts created
    // through template documents aren't worth executing
    // so it became this ... hopefully it won't hurt in the wild
    var script = document.createElement(nodeName);
    length = attributes.length;
    i = 0;
    while (i < length)
      script.setAttributeNode(attributes[i++].cloneNode(true));
    script.textContent = node.textContent;
    node.parentNode.replaceChild(script, node);
  }
}

function Any(node, path) {
  return {
    type: 'any',
    node: node,
    path: path
  };
}

function Attr(node, path, name, sparse) {
  return {
    type: 'attr',
    node: node,
    path: path,
    name: name,
    sparse: sparse
  };
}

function Text(node, path) {
  return {
    type: 'text',
    node: node,
    path: path
  };
}

},{"@ungap/trim":18,"domconstants":22}],28:[function(require,module,exports){
'use strict';
/*! (C) 2017-2018 Andrea Giammarchi - ISC Style License */

const {Component, bind, define, hyper, wire} = require('hyperhtml');

// utils to deal with custom elements builtin extends
const ATTRIBUTE_CHANGED_CALLBACK = 'attributeChangedCallback';
const O = Object;
const classes = [];
const defineProperty = O.defineProperty;
const getOwnPropertyDescriptor = O.getOwnPropertyDescriptor;
const getOwnPropertyNames = O.getOwnPropertyNames;
const getOwnPropertySymbols = O.getOwnPropertySymbols || (() => []);
const getPrototypeOf = O.getPrototypeOf || (o => o.__proto__);
const ownKeys = typeof Reflect === 'object' && Reflect.ownKeys ||
                (o => getOwnPropertyNames(o).concat(getOwnPropertySymbols(o)));
const setPrototypeOf = O.setPrototypeOf ||
                      ((o, p) => (o.__proto__ = p, o));
const camel = name => name.replace(/-([a-z])/g, ($0, $1) => $1.toUpperCase());
const {attachShadow} = HTMLElement.prototype;
const sr = new WeakMap;

class HyperHTMLElement extends HTMLElement {

  // define a custom-element in the CustomElementsRegistry
  // class MyEl extends HyperHTMLElement {}
  // MyEl.define('my-el');
  static define(name, options) {
    const Class = this;
    const proto = Class.prototype;

    const onChanged = proto[ATTRIBUTE_CHANGED_CALLBACK];
    const hasChange = !!onChanged;

    // Class.booleanAttributes
    // -----------------------------------------------
    // attributes defined as boolean will have
    // an either available or not available attribute
    // regardless of the value.
    // All falsy values, or "false", mean attribute removed
    // while truthy values will be set as is.
    // Boolean attributes are also automatically observed.
    const booleanAttributes = Class.booleanAttributes || [];
    booleanAttributes.forEach(name => {
      if (!(name in proto)) defineProperty(
        proto,
        camel(name),
        {
          configurable: true,
          get() {
            return this.hasAttribute(name);
          },
          set(value) {
            if (!value || value === 'false')
              this.removeAttribute(name);
            else
              this.setAttribute(name, value);
          }
        }
      );
    });

    // Class.observedAttributes
    // -------------------------------------------------------
    // HyperHTMLElement will directly reflect get/setAttribute
    // operation once these attributes are used, example:
    // el.observed = 123;
    // will automatically do
    // el.setAttribute('observed', 123);
    // triggering also the attributeChangedCallback
    const observedAttributes = Class.observedAttributes || [];
    observedAttributes.forEach(name => {
      // it is possible to redefine the behavior at any time
      // simply overwriting get prop() and set prop(value)
      if (!(name in proto)) defineProperty(
        proto,
        camel(name),
        {
          configurable: true,
          get() {
            return this.getAttribute(name);
          },
          set(value) {
            if (value == null)
              this.removeAttribute(name);
            else
              this.setAttribute(name, value);
          }
        }
      );
    });

    // if these are defined, overwrite the observedAttributes getter
    // to include also booleanAttributes
    const attributes = booleanAttributes.concat(observedAttributes);
    if (attributes.length)
      defineProperty(Class, 'observedAttributes', {
        get() { return attributes; }
      });

    // created() {}
    // ---------------------------------
    // an initializer method that grants
    // the node is fully known to the browser.
    // It is ensured to run either after DOMContentLoaded,
    // or once there is a next sibling (stream-friendly) so that
    // you have full access to element attributes and/or childNodes.
    const created = proto.created || function () {
      this.render();
    };

    // used to ensure create() is called once and once only
    defineProperty(
      proto,
      '_init$',
      {
        configurable: true,
        writable: true,
        value: true
      }
    );

    defineProperty(
      proto,
      ATTRIBUTE_CHANGED_CALLBACK,
      {
        configurable: true,
        value: function aCC(name, prev, curr) {
          if (this._init$) {
            checkReady.call(this, created);
            if (this._init$)
              return this._init$$.push(aCC.bind(this, name, prev, curr));
          }
          // ensure setting same value twice
          // won't trigger twice attributeChangedCallback
          if (hasChange && prev !== curr) {
            onChanged.apply(this, arguments);
          }
        }
      }
    );

    const onConnected = proto.connectedCallback;
    const hasConnect = !!onConnected;
    defineProperty(
      proto,
      'connectedCallback',
      {
        configurable: true,
        value: function cC() {
          if (this._init$) {
            checkReady.call(this, created);
            if (this._init$)
              return this._init$$.push(cC.bind(this));
          }
          if (hasConnect) {
            onConnected.apply(this, arguments);
          }
        }
      }
    );

    // define lazily all handlers
    // class { handleClick() { ... }
    // render() { `<a onclick=${this.handleClick}>` } }
    getOwnPropertyNames(proto).forEach(key => {
      if (/^handle[A-Z]/.test(key)) {
        const _key$ = '_' + key + '$';
        const method = proto[key];
        defineProperty(proto, key, {
          configurable: true,
          get() {
            return  this[_key$] ||
                    (this[_key$] = method.bind(this));
          }
        });
      }
    });

    // whenever you want to directly use the component itself
    // as EventListener, you can pass it directly.
    // https://medium.com/@WebReflection/dom-handleevent-a-cross-platform-standard-since-year-2000-5bf17287fd38
    //  class Reactive extends HyperHTMLElement {
    //    oninput(e) { console.log(this, 'changed', e.target.value); }
    //    render() { this.html`<input oninput="${this}">`; }
    //  }
    if (!('handleEvent' in proto)) {
      defineProperty(
        proto,
        'handleEvent',
        {
          configurable: true,
          value(event) {
            this[
              (event.currentTarget.dataset || {}).call ||
              ('on' + event.type)
            ](event);
          }
        }
      );
    }

    if (options && options.extends) {
      const Native = document.createElement(options.extends).constructor;
      const Intermediate = class extends Native {};
      const ckeys = ['length', 'name', 'arguments', 'caller', 'prototype'];
      const pkeys = [];
      let Super = null;
      let BaseClass = Class;
      while (Super = getPrototypeOf(BaseClass)) {
        [
          {target: Intermediate, base: Super, keys: ckeys},
          {target: Intermediate.prototype, base: Super.prototype, keys: pkeys}
        ]
        .forEach(({target, base, keys}) => {
          ownKeys(base)
            .filter(key => keys.indexOf(key) < 0)
            .forEach((key) => {
              keys.push(key);
              defineProperty(
                target,
                key,
                getOwnPropertyDescriptor(base, key)
              );
            });
        });

        BaseClass = Super;
        if (Super === HyperHTMLElement)
          break;
      }
      setPrototypeOf(Class, Intermediate);
      setPrototypeOf(proto, Intermediate.prototype);
      customElements.define(name, Class, options);
    } else {
      customElements.define(name, Class);
    }
    classes.push(Class);
    return Class;
  }

  // weakly relate the shadowRoot for refs usage
  attachShadow() {
    const shadowRoot = attachShadow.apply(this, arguments);
    sr.set(this, shadowRoot);
    return shadowRoot;
  }

  // returns elements by ref
  get refs() {
    const value = {};
    if ('_html$' in this) {
      const all = (sr.get(this) || this).querySelectorAll('[ref]');
      for (let {length} = all, i = 0; i < length; i++) {
        const node = all[i];
        value[node.getAttribute('ref')] = node;
      }
      Object.defineProperty(this, 'refs', {value});
      return value;
    }
    return value;
  }

  // lazily bind once hyperHTML logic
  // to either the shadowRoot, if present and open,
  // the _shadowRoot property, if set due closed shadow root,
  // or the custom-element itself if no Shadow DOM is used.
  get html() {
    return this._html$ || (this.html = bind(
      // in a way or another, bind to the right node
      // backward compatible, first two could probably go already
      this.shadowRoot || this._shadowRoot || sr.get(this) || this
    ));
  }

  // it can be set too if necessary, it won't invoke render()
  set html(value) {
    defineProperty(this, '_html$', {configurable: true, value: value});
  }

  // overwrite this method with your own render
  render() {}

  // ---------------------//
  // Basic State Handling //
  // ---------------------//

  // define the default state object
  // you could use observed properties too
  get defaultState() { return {}; }

  // the state with a default
  get state() {
    return this._state$ || (this.state = this.defaultState);
  }

  // it can be set too if necessary, it won't invoke render()
  set state(value) {
    defineProperty(this, '_state$', {configurable: true, value: value});
  }

  // currently a state is a shallow copy, like in Preact or other libraries.
  // after the state is updated, the render() method will be invoked.
  // ⚠️ do not ever call this.setState() inside this.render()
  setState(state, render) {
    const target = this.state;
    const source = typeof state === 'function' ? state.call(this, target) : state;
    for (const key in source) target[key] = source[key];
    if (render !== false) this.render();
    return this;
  }

};

// exposing hyperHTML utilities
HyperHTMLElement.Component = Component;
HyperHTMLElement.bind = bind;
HyperHTMLElement.intent = define;
HyperHTMLElement.wire = wire;
HyperHTMLElement.hyper = hyper;

try {
  if (Symbol.hasInstance) classes.push(
    defineProperty(HyperHTMLElement, Symbol.hasInstance, {
      enumerable: false,
      configurable: true,
      value(instance) {
        return classes.some(isPrototypeOf, getPrototypeOf(instance));
      }
    }));
} catch(meh) {}

Object.defineProperty(exports, '__esModule', {value: true}).default = HyperHTMLElement;

// ------------------------------//
// DOMContentLoaded VS created() //
// ------------------------------//
const dom = {
  type: 'DOMContentLoaded',
  handleEvent() {
    if (dom.ready()) {
      document.removeEventListener(dom.type, dom, false);
      dom.list.splice(0).forEach(invoke);
    }
    else
      setTimeout(dom.handleEvent);
  },
  ready() {
    return document.readyState === 'complete';
  },
  list: []
};

if (!dom.ready()) {
  document.addEventListener(dom.type, dom, false);
}

function checkReady(created) {
  if (dom.ready() || isReady.call(this, created)) {
    if (this._init$) {
      const list = this._init$$;
      if (list) delete this._init$$;
      created.call(defineProperty(this, '_init$', {value: false}));
      if (list) list.forEach(invoke);
    }
  } else {
    if (!this.hasOwnProperty('_init$$'))
      defineProperty(this, '_init$$', {configurable: true, value: []});
    dom.list.push(checkReady.bind(this, created));
  }
}

function invoke(fn) {
  fn();
}

function isPrototypeOf(Class) {
  return this === Class.prototype;
}

function isReady(created) {
  let el = this;
  do { if (el.nextSibling) return true; }
  while (el = el.parentNode);
  setTimeout(checkReady.bind(this, created));
  return false;
}

},{"hyperhtml":34}],29:[function(require,module,exports){
/*! (c) Andrea Giammarchi - ISC */
var hyperStyle = (function (){'use strict';
  // from https://github.com/developit/preact/blob/33fc697ac11762a1cb6e71e9847670d047af7ce5/src/varants.js
  var IS_NON_DIMENSIONAL = /acit|ex(?:s|g|n|p|$)|rph|ows|mnc|ntw|ine[ch]|zoo|^ord/i;
  var hyphen = /([^A-Z])([A-Z]+)/g;
  return function hyperStyle(node, original) {
    return 'ownerSVGElement' in node ? svg(node, original) : update(node.style, false);
  };
  function ized($0, $1, $2) {
    return $1 + '-' + $2.toLowerCase();
  }
  function svg(node, original) {
    var style;
    if (original)
      style = original.cloneNode(true);
    else {
      node.setAttribute('style', '--hyper:style;');
      style = node.getAttributeNode('style');
    }
    style.value = '';
    node.setAttributeNode(style);
    return update(style, true);
  }
  function toStyle(object) {
    var key, css = [];
    for (key in object)
      css.push(key.replace(hyphen, ized), ':', object[key], ';');
    return css.join('');
  }
  function update(style, isSVG) {
    var oldType, oldValue;
    return function (newValue) {
      var info, key, styleValue, value;
      switch (typeof newValue) {
        case 'object':
          if (newValue) {
            if (oldType === 'object') {
              if (!isSVG) {
                if (oldValue !== newValue) {
                  for (key in oldValue) {
                    if (!(key in newValue)) {
                      style[key] = '';
                    }
                  }
                }
              }
            } else {
              if (isSVG)
                style.value = '';
              else
                style.cssText = '';
            }
            info = isSVG ? {} : style;
            for (key in newValue) {
              value = newValue[key];
              styleValue = typeof value === 'number' &&
                                  !IS_NON_DIMENSIONAL.test(key) ?
                                  (value + 'px') : value;
              if (!isSVG && /^--/.test(key))
                info.setProperty(key, styleValue);
              else
                info[key] = styleValue;
            }
            oldType = 'object';
            if (isSVG)
              style.value = toStyle((oldValue = info));
            else
              oldValue = newValue;
            break;
          }
        default:
          if (oldValue != newValue) {
            oldType = 'string';
            oldValue = newValue;
            if (isSVG)
              style.value = newValue || '';
            else
              style.cssText = newValue || '';
          }
          break;
      }
    };
  }
}());
module.exports = hyperStyle;

},{}],30:[function(require,module,exports){
/*! (c) Andrea Giammarchi - ISC */
var Wire = (function (slice, proto) {

  proto = Wire.prototype;

  proto.ELEMENT_NODE = 1;
  proto.nodeType = 111;

  proto.remove = function (keepFirst) {
    var childNodes = this.childNodes;
    var first = this.firstChild;
    var last = this.lastChild;
    this._ = null;
    if (keepFirst && childNodes.length === 2) {
      last.parentNode.removeChild(last);
    } else {
      var range = this.ownerDocument.createRange();
      range.setStartBefore(keepFirst ? childNodes[1] : first);
      range.setEndAfter(last);
      range.deleteContents();
    }
    return first;
  };

  proto.valueOf = function (forceAppend) {
    var fragment = this._;
    var noFragment = fragment == null;
    if (noFragment)
      fragment = (this._ = this.ownerDocument.createDocumentFragment());
    if (noFragment || forceAppend) {
      for (var n = this.childNodes, i = 0, l = n.length; i < l; i++)
        fragment.appendChild(n[i]);
    }
    return fragment;
  };

  return Wire;

  function Wire(childNodes) {
    var nodes = (this.childNodes = slice.call(childNodes, 0));
    this.firstChild = nodes[0];
    this.lastChild = nodes[nodes.length - 1];
    this.ownerDocument = nodes[0].ownerDocument;
    this._ = null;
  }

}([].slice));
module.exports = Wire;

},{}],31:[function(require,module,exports){
'use strict';
const CustomEvent = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('@ungap/custom-event'));
const Map = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('@ungap/essential-map'));
const WeakMap = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('@ungap/weakmap'));

// hyperHTML.Component is a very basic class
// able to create Custom Elements like components
// including the ability to listen to connect/disconnect
// events via onconnect/ondisconnect attributes
// Components can be created imperatively or declaratively.
// The main difference is that declared components
// will not automatically render on setState(...)
// to simplify state handling on render.
function Component() {
  return this; // this is needed in Edge !!!
}
Object.defineProperty(exports, '__esModule', {value: true}).default = Component

// Component is lazily setup because it needs
// wire mechanism as lazy content
function setup(content) {
  // there are various weakly referenced variables in here
  // and mostly are to use Component.for(...) static method.
  const children = new WeakMap;
  const create = Object.create;
  const createEntry = (wm, id, component) => {
    wm.set(id, component);
    return component;
  };
  const get = (Class, info, context, id) => {
    const relation = info.get(Class) || relate(Class, info);
    switch (typeof id) {
      case 'object':
      case 'function':
        const wm = relation.w || (relation.w = new WeakMap);
        return wm.get(id) || createEntry(wm, id, new Class(context));
      default:
        const sm = relation.p || (relation.p = create(null));
        return sm[id] || (sm[id] = new Class(context));
    }
  };
  const relate = (Class, info) => {
    const relation = {w: null, p: null};
    info.set(Class, relation);
    return relation;
  };
  const set = context => {
    const info = new Map;
    children.set(context, info);
    return info;
  };
  // The Component Class
  Object.defineProperties(
    Component,
    {
      // Component.for(context[, id]) is a convenient way
      // to automatically relate data/context to children components
      // If not created yet, the new Component(context) is weakly stored
      // and after that same instance would always be returned.
      for: {
        configurable: true,
        value(context, id) {
          return get(
            this,
            children.get(context) || set(context),
            context,
            id == null ?
              'default' : id
          );
        }
      }
    }
  );
  Object.defineProperties(
    Component.prototype,
    {
      // all events are handled with the component as context
      handleEvent: {value(e) {
        const ct = e.currentTarget;
        this[
          ('getAttribute' in ct && ct.getAttribute('data-call')) ||
          ('on' + e.type)
        ](e);
      }},
      // components will lazily define html or svg properties
      // as soon as these are invoked within the .render() method
      // Such render() method is not provided by the base class
      // but it must be available through the Component extend.
      // Declared components could implement a
      // render(props) method too and use props as needed.
      html: lazyGetter('html', content),
      svg: lazyGetter('svg', content),
      // the state is a very basic/simple mechanism inspired by Preact
      state: lazyGetter('state', function () { return this.defaultState; }),
      // it is possible to define a default state that'd be always an object otherwise
      defaultState: {get() { return {}; }},
      // dispatch a bubbling, cancelable, custom event
      // through the first known/available node
      dispatch: {value(type, detail) {
        const {_wire$} = this;
        if (_wire$) {
          const event = new CustomEvent(type, {
            bubbles: true,
            cancelable: true,
            detail
          });
          event.component = this;
          return (_wire$.dispatchEvent ?
                    _wire$ :
                    _wire$.firstChild
                  ).dispatchEvent(event);
        }
        return false;
      }},
      // setting some property state through a new object
      // or a callback, triggers also automatically a render
      // unless explicitly specified to not do so (render === false)
      setState: {value(state, render) {
        const target = this.state;
        const source = typeof state === 'function' ? state.call(this, target) : state;
        for (const key in source) target[key] = source[key];
        if (render !== false)
          this.render();
        return this;
      }}
    }
  );
}
exports.setup = setup

// instead of a secret key I could've used a WeakMap
// However, attaching a property directly will result
// into better performance with thousands of components
// hanging around, and less memory pressure caused by the WeakMap
const lazyGetter = (type, fn) => {
  const secret = '_' + type + '$';
  return {
    get() {
      return this[secret] || setValue(this, secret, fn.call(this, type));
    },
    set(value) {
      setValue(this, secret, value);
    }
  };
};

// shortcut to set value on get or set(value)
const setValue = (self, secret, value) =>
  Object.defineProperty(self, secret, {
    configurable: true,
    value: typeof value === 'function' ?
      function () {
        return (self._wire$ = value.apply(this, arguments));
      } :
      value
  })[secret]
;

Object.defineProperties(
  Component.prototype,
  {
    // used to distinguish better than instanceof
    ELEMENT_NODE: {value: 1},
    nodeType: {value: -1}
  }
);

},{"@ungap/custom-event":11,"@ungap/essential-map":12,"@ungap/weakmap":19}],32:[function(require,module,exports){
'use strict';
const WeakMap = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('@ungap/weakmap'));
const tta = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('@ungap/template-tag-arguments'));

const {OWNER_SVG_ELEMENT} = require('../shared/constants.js');
const {Tagger} = require('../objects/Updates.js');

// a weak collection of contexts that
// are already known to hyperHTML
const bewitched = new WeakMap;

// better known as hyper.bind(node), the render is
// the main tag function in charge of fully upgrading
// or simply updating, contexts used as hyperHTML targets.
// The `this` context is either a regular DOM node or a fragment.
function render() {
  const wicked = bewitched.get(this);
  const args = tta.apply(null, arguments);
  if (wicked && wicked.template === args[0]) {
    wicked.tagger.apply(null, args);
  } else {
    upgrade.apply(this, args);
  }
  return this;
}

// an upgrade is in charge of collecting template info,
// parse it once, if unknown, to map all interpolations
// as single DOM callbacks, relate such template
// to the current context, and render it after cleaning the context up
function upgrade(template) {
  const type = OWNER_SVG_ELEMENT in this ? 'svg' : 'html';
  const tagger = new Tagger(type);
  bewitched.set(this, {tagger, template: template});
  this.textContent = '';
  this.appendChild(tagger.apply(null, arguments));
}

Object.defineProperty(exports, '__esModule', {value: true}).default = render;

},{"../objects/Updates.js":36,"../shared/constants.js":37,"@ungap/template-tag-arguments":17,"@ungap/weakmap":19}],33:[function(require,module,exports){
'use strict';
const WeakMap = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('@ungap/weakmap'));
const tta = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('@ungap/template-tag-arguments'));

const Wire = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('hyperhtml-wire'));

const {Tagger} = require('../objects/Updates.js');

// all wires used per each context
const wires = new WeakMap;

// A wire is a callback used as tag function
// to lazily relate a generic object to a template literal.
// hyper.wire(user)`<div id=user>${user.name}</div>`; => the div#user
// This provides the ability to have a unique DOM structure
// related to a unique JS object through a reusable template literal.
// A wire can specify a type, as svg or html, and also an id
// via html:id or :id convention. Such :id allows same JS objects
// to be associated to different DOM structures accordingly with
// the used template literal without losing previously rendered parts.
const wire = (obj, type) => obj == null ?
  content(type || 'html') :
  weakly(obj, type || 'html');

// A wire content is a virtual reference to one or more nodes.
// It's represented by either a DOM node, or an Array.
// In both cases, the wire content role is to simply update
// all nodes through the list of related callbacks.
// In few words, a wire content is like an invisible parent node
// in charge of updating its content like a bound element would do.
const content = type => {
  let wire, tagger, template;
  return function () {
    const args = tta.apply(null, arguments);
    if (template !== args[0]) {
      template = args[0];
      tagger = new Tagger(type);
      wire = wireContent(tagger.apply(tagger, args));
    } else {
      tagger.apply(tagger, args);
    }
    return wire;
  };
};

// wires are weakly created through objects.
// Each object can have multiple wires associated
// and this is thanks to the type + :id feature.
const weakly = (obj, type) => {
  const i = type.indexOf(':');
  let wire = wires.get(obj);
  let id = type;
  if (-1 < i) {
    id = type.slice(i + 1);
    type = type.slice(0, i) || 'html';
  }
  if (!wire)
    wires.set(obj, wire = {});
  return wire[id] || (wire[id] = content(type));
};

// A document fragment loses its nodes 
// as soon as it is appended into another node.
// This has the undesired effect of losing wired content
// on a second render call, because (by then) the fragment would be empty:
// no longer providing access to those sub-nodes that ultimately need to
// stay associated with the original interpolation.
// To prevent hyperHTML from forgetting about a fragment's sub-nodes,
// fragments are instead returned as an Array of nodes or, if there's only one entry,
// as a single referenced node which, unlike fragments, will indeed persist
// wire content throughout multiple renderings.
// The initial fragment, at this point, would be used as unique reference to this
// array of nodes or to this single referenced node.
const wireContent = node => {
  const childNodes = node.childNodes;
  const {length} = childNodes;
  return length === 1 ?
    childNodes[0] :
    (length ? new Wire(childNodes) : node);
};

exports.content = content;
exports.weakly = weakly;
Object.defineProperty(exports, '__esModule', {value: true}).default = wire;

},{"../objects/Updates.js":36,"@ungap/template-tag-arguments":17,"@ungap/weakmap":19,"hyperhtml-wire":30}],34:[function(require,module,exports){
'use strict';
/*! (c) Andrea Giammarchi (ISC) */
const WeakMap = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('@ungap/weakmap'));
const WeakSet = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('@ungap/essential-weakset'));

const diff = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('domdiff'));
const Component = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('./classes/Component.js'));
const {setup} = require('./classes/Component.js');
const Intent = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('./objects/Intent.js'));
const {observe, Tagger} = require('./objects/Updates.js');
const wire = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('./hyper/wire.js'));
const {content, weakly} = require('./hyper/wire.js');
const render = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('./hyper/render.js'));

// all functions are self bound to the right context
// you can do the following
// const {bind, wire} = hyperHTML;
// and use them right away: bind(node)`hello!`;
const bind = context => render.bind(context);
const define = Intent.define;
const tagger = Tagger.prototype;

hyper.Component = Component;
hyper.bind = bind;
hyper.define = define;
hyper.diff = diff;
hyper.hyper = hyper;
hyper.observe = observe;
hyper.tagger = tagger;
hyper.wire = wire;

// exported as shared utils
// for projects based on hyperHTML
// that don't necessarily need upfront polyfills
// i.e. those still targeting IE
hyper._ = {
  WeakMap,
  WeakSet
};

// the wire content is the lazy defined
// html or svg property of each hyper.Component
setup(content);

// everything is exported directly or through the
// hyperHTML callback, when used as top level script
exports.Component = Component;
exports.bind = bind;
exports.define = define;
exports.diff = diff;
exports.hyper = hyper;
exports.observe = observe;
exports.tagger = tagger;
exports.wire = wire;

// by default, hyperHTML is a smart function
// that "magically" understands what's the best
// thing to do with passed arguments
function hyper(HTML) {
  return arguments.length < 2 ?
    (HTML == null ?
      content('html') :
      (typeof HTML === 'string' ?
        hyper.wire(null, HTML) :
        ('raw' in HTML ?
          content('html')(HTML) :
          ('nodeType' in HTML ?
            hyper.bind(HTML) :
            weakly(HTML, 'html')
          )
        )
      )) :
    ('raw' in HTML ?
      content('html') : hyper.wire
    ).apply(null, arguments);
}
Object.defineProperty(exports, '__esModule', {value: true}).default = hyper

},{"./classes/Component.js":31,"./hyper/render.js":32,"./hyper/wire.js":33,"./objects/Intent.js":35,"./objects/Updates.js":36,"@ungap/essential-weakset":13,"@ungap/weakmap":19,"domdiff":23}],35:[function(require,module,exports){
'use strict';
const attributes = {};
const intents = {};
const keys = [];
const hasOwnProperty = intents.hasOwnProperty;

let length = 0;

Object.defineProperty(exports, '__esModule', {value: true}).default = {

  // used to invoke right away hyper:attributes
  attributes,

  // hyperHTML.define('intent', (object, update) => {...})
  // can be used to define a third parts update mechanism
  // when every other known mechanism failed.
  // hyper.define('user', info => info.name);
  // hyper(node)`<p>${{user}}</p>`;
  define: (intent, callback) => {
    if (intent.indexOf('-') < 0) {
      if (!(intent in intents)) {
        length = keys.push(intent);
      }
      intents[intent] = callback;
    } else {
      attributes[intent] = callback;
    }
  },

  // this method is used internally as last resort
  // to retrieve a value out of an object
  invoke: (object, callback) => {
    for (let i = 0; i < length; i++) {
      let key = keys[i];
      if (hasOwnProperty.call(object, key)) {
        return intents[key](object[key], callback);
      }
    }
  }
};

},{}],36:[function(require,module,exports){
'use strict';
const CustomEvent = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('@ungap/custom-event'));
const WeakSet = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('@ungap/essential-weakset'));
const isArray = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('@ungap/is-array'));
const createContent = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('@ungap/create-content'));

const disconnected = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('disconnected'));
const domdiff = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('domdiff'));
const domtagger = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('domtagger'));
const hyperStyle = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('hyperhtml-style'));
const Wire = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('hyperhtml-wire'));

const {
  CONNECTED, DISCONNECTED, DOCUMENT_FRAGMENT_NODE, OWNER_SVG_ELEMENT
} = require('../shared/constants.js');

const Component = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('../classes/Component.js'));
const Intent = (m => m.__esModule ? /* istanbul ignore next */ m.default : /* istanbul ignore next */ m)(require('./Intent.js'));

const componentType = Component.prototype.nodeType;
const wireType = Wire.prototype.nodeType;

const observe = disconnected({Event: CustomEvent, WeakSet});

exports.Tagger = Tagger;
exports.observe = observe;

// returns an intent to explicitly inject content as html
const asHTML = html => ({html});

// returns nodes from wires and components
const asNode = (item, i) => {
  switch (item.nodeType) {
    case wireType:
      // in the Wire case, the content can be
      // removed, post-pended, inserted, or pre-pended and
      // all these cases are handled by domdiff already
      /* istanbul ignore next */
      return (1 / i) < 0 ?
        (i ? item.remove(true) : item.lastChild) :
        (i ? item.valueOf(true) : item.firstChild);
    case componentType:
      return asNode(item.render(), i);
    default:
      return item;
  }
}

// returns true if domdiff can handle the value
const canDiff = value => 'ELEMENT_NODE' in value;

const hyperSetter = (node, name, svg) => svg ?
  value => {
    try {
      node[name] = value;
    }
    catch (nope) {
      node.setAttribute(name, value);
    }
  } :
  value => {
    node[name] = value;
  };

// when a Promise is used as interpolation value
// its result must be parsed once resolved.
// This callback is in charge of understanding what to do
// with a returned value once the promise is resolved.
const invokeAtDistance = (value, callback) => {
  callback(value.placeholder);
  if ('text' in value) {
    Promise.resolve(value.text).then(String).then(callback);
  } else if ('any' in value) {
    Promise.resolve(value.any).then(callback);
  } else if ('html' in value) {
    Promise.resolve(value.html).then(asHTML).then(callback);
  } else {
    Promise.resolve(Intent.invoke(value, callback)).then(callback);
  }
};

// quick and dirty way to check for Promise/ish values
const isPromise_ish = value => value != null && 'then' in value;

// list of attributes that should not be directly assigned
const readOnly = /^(?:form|list)$/i;

// reused every slice time
const slice = [].slice;

// simplifies text node creation
const text = (node, text) => node.ownerDocument.createTextNode(text);

function Tagger(type) {
  this.type = type;
  return domtagger(this);
}

Tagger.prototype = {

  // there are four kind of attributes, and related behavior:
  //  * events, with a name starting with `on`, to add/remove event listeners
  //  * special, with a name present in their inherited prototype, accessed directly
  //  * regular, accessed through get/setAttribute standard DOM methods
  //  * style, the only regular attribute that also accepts an object as value
  //    so that you can style=${{width: 120}}. In this case, the behavior has been
  //    fully inspired by Preact library and its simplicity.
  attribute(node, name, original) {
    const isSVG = OWNER_SVG_ELEMENT in node;
    let oldValue;
    // if the attribute is the style one
    // handle it differently from others
    if (name === 'style')
      return hyperStyle(node, original, isSVG);
    // direct accessors for <input .value=${...}> and friends
    else if (name.slice(0, 1) === '.')
      return hyperSetter(node, name.slice(1), isSVG);
    // the name is an event one,
    // add/remove event listeners accordingly
    else if (/^on/.test(name)) {
      let type = name.slice(2);
      if (type === CONNECTED || type === DISCONNECTED) {
        observe(node);
      }
      else if (name.toLowerCase()
        in node) {
        type = type.toLowerCase();
      }
      return newValue => {
        if (oldValue !== newValue) {
          if (oldValue)
            node.removeEventListener(type, oldValue, false);
          oldValue = newValue;
          if (newValue)
            node.addEventListener(type, newValue, false);
        }
      };
    }
    // the attribute is special ('value' in input)
    // and it's not SVG *or* the name is exactly data,
    // in this case assign the value directly
    else if (
      name === 'data' ||
      (!isSVG && name in node && !readOnly.test(name))
    ) {
      return newValue => {
        if (oldValue !== newValue) {
          oldValue = newValue;
          if (node[name] !== newValue && newValue == null) {
            // cleanup on null to avoid silly IE/Edge bug
            node[name] = '';
            node.removeAttribute(name);
          }
          else
            node[name] = newValue;
        }
      };
    }
    else if (name in Intent.attributes) {
      oldValue;
      return any => {
        const newValue = Intent.attributes[name](node, any);
        if (oldValue !== newValue) {
          oldValue = newValue;
          if (newValue == null)
            node.removeAttribute(name);
          else
            node.setAttribute(name, newValue);
        }
      };
    }
    // in every other case, use the attribute node as it is
    // update only the value, set it as node only when/if needed
    else {
      let owner = false;
      const attribute = original.cloneNode(true);
      return newValue => {
        if (oldValue !== newValue) {
          oldValue = newValue;
          if (attribute.value !== newValue) {
            if (newValue == null) {
              if (owner) {
                owner = false;
                node.removeAttributeNode(attribute);
              }
              attribute.value = newValue;
            } else {
              attribute.value = newValue;
              if (!owner) {
                owner = true;
                node.setAttributeNode(attribute);
              }
            }
          }
        }
      };
    }
  },

  // in a hyper(node)`<div>${content}</div>` case
  // everything could happen:
  //  * it's a JS primitive, stored as text
  //  * it's null or undefined, the node should be cleaned
  //  * it's a component, update the content by rendering it
  //  * it's a promise, update the content once resolved
  //  * it's an explicit intent, perform the desired operation
  //  * it's an Array, resolve all values if Promises and/or
  //    update the node with the resulting list of content
  any(node, childNodes) {
    const diffOptions = {node: asNode, before: node};
    const nodeType = OWNER_SVG_ELEMENT in node ? /* istanbul ignore next */ 'svg' : 'html';
    let fastPath = false;
    let oldValue;
    const anyContent = value => {
      switch (typeof value) {
        case 'string':
        case 'number':
        case 'boolean':
          if (fastPath) {
            if (oldValue !== value) {
              oldValue = value;
              childNodes[0].textContent = value;
            }
          } else {
            fastPath = true;
            oldValue = value;
            childNodes = domdiff(
              node.parentNode,
              childNodes,
              [text(node, value)],
              diffOptions
            );
          }
          break;
        case 'function':
          anyContent(value(node));
          break;
        case 'object':
        case 'undefined':
          if (value == null) {
            fastPath = false;
            childNodes = domdiff(
              node.parentNode,
              childNodes,
              [],
              diffOptions
            );
            break;
          }
        default:
          fastPath = false;
          oldValue = value;
          if (isArray(value)) {
            if (value.length === 0) {
              if (childNodes.length) {
                childNodes = domdiff(
                  node.parentNode,
                  childNodes,
                  [],
                  diffOptions
                );
              }
            } else {
              switch (typeof value[0]) {
                case 'string':
                case 'number':
                case 'boolean':
                  anyContent({html: value});
                  break;
                case 'object':
                  if (isArray(value[0])) {
                    value = value.concat.apply([], value);
                  }
                  if (isPromise_ish(value[0])) {
                    Promise.all(value).then(anyContent);
                    break;
                  }
                default:
                  childNodes = domdiff(
                    node.parentNode,
                    childNodes,
                    value,
                    diffOptions
                  );
                  break;
              }
            }
          } else if (canDiff(value)) {
            childNodes = domdiff(
              node.parentNode,
              childNodes,
              value.nodeType === DOCUMENT_FRAGMENT_NODE ?
                slice.call(value.childNodes) :
                [value],
              diffOptions
            );
          } else if (isPromise_ish(value)) {
            value.then(anyContent);
          } else if ('placeholder' in value) {
            invokeAtDistance(value, anyContent);
          } else if ('text' in value) {
            anyContent(String(value.text));
          } else if ('any' in value) {
            anyContent(value.any);
          } else if ('html' in value) {
            childNodes = domdiff(
              node.parentNode,
              childNodes,
              slice.call(
                createContent(
                  [].concat(value.html).join(''),
                  nodeType
                ).childNodes
              ),
              diffOptions
            );
          } else if ('length' in value) {
            anyContent(slice.call(value));
          } else {
            anyContent(Intent.invoke(value, anyContent));
          }
          break;
      }
    };
    return anyContent;
  },

  // style or textareas don't accept HTML as content
  // it's pointless to transform or analyze anything
  // different from text there but it's worth checking
  // for possible defined intents.
  text(node) {
    let oldValue;
    const textContent = value => {
      if (oldValue !== value) {
        oldValue = value;
        const type = typeof value;
        if (type === 'object' && value) {
          if (isPromise_ish(value)) {
            value.then(textContent);
          } else if ('placeholder' in value) {
            invokeAtDistance(value, textContent);
          } else if ('text' in value) {
            textContent(String(value.text));
          } else if ('any' in value) {
            textContent(value.any);
          } else if ('html' in value) {
            textContent([].concat(value.html).join(''));
          } else if ('length' in value) {
            textContent(slice.call(value).join(''));
          } else {
            textContent(Intent.invoke(value, textContent));
          }
        } else if (type === 'function') {
          textContent(value(node));
        } else {
          node.textContent = value == null ? '' : value;
        }
      }
    };
    return textContent;
  }
};

},{"../classes/Component.js":31,"../shared/constants.js":37,"./Intent.js":35,"@ungap/create-content":10,"@ungap/custom-event":11,"@ungap/essential-weakset":13,"@ungap/is-array":15,"disconnected":20,"domdiff":23,"domtagger":26,"hyperhtml-style":29,"hyperhtml-wire":30}],37:[function(require,module,exports){
'use strict';
// Node.CONSTANTS
// 'cause some engine has no global Node defined
// (i.e. Node, NativeScript, basicHTML ... )
const ELEMENT_NODE = 1;
exports.ELEMENT_NODE = ELEMENT_NODE;
const DOCUMENT_FRAGMENT_NODE = 11;
exports.DOCUMENT_FRAGMENT_NODE = DOCUMENT_FRAGMENT_NODE;

// SVG related constants
const OWNER_SVG_ELEMENT = 'ownerSVGElement';
exports.OWNER_SVG_ELEMENT = OWNER_SVG_ELEMENT;

// Custom Elements / MutationObserver constants
const CONNECTED = 'connected';
exports.CONNECTED = CONNECTED;
const DISCONNECTED = 'dis' + CONNECTED;
exports.DISCONNECTED = DISCONNECTED;

},{}],38:[function(require,module,exports){
'use strict';
const {isArray} = Array;
const {indexOf, slice} = [];

exports.isArray = isArray;
exports.indexOf = indexOf;
exports.slice = slice;

},{}],39:[function(require,module,exports){
'use strict';
module.exports = _ => ({
  // About: get: _.get.bind(_)
  // It looks like WebKit/Safari didn't optimize bind at all,
  // so that using bind slows it down by 60%.
  // Firefox and Chrome are just fine in both cases,
  // so let's use the approach that works fast everywhere 👍
  get: key => _.get(key),
  set: (key, value) => (_.set(key, value), value)
});

},{}]},{},[9]);
