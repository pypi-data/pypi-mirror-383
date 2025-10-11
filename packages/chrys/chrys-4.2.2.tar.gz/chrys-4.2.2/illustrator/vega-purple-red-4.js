var config = {"document":{"height":210,"width":297,"mode":"rgb"},"characterStyles":[{"name":"swatchRectTitle","attributes":{"size":8}}],"swatchRect":{"textPosition":0.125},"colors":[{"group":"vega-purple-red-4","name":"vega-purple-red-4-1","rgb":[206,158,204]},{"group":"vega-purple-red-4","name":"vega-purple-red-4-2","rgb":[218,107,178]},{"group":"vega-purple-red-4","name":"vega-purple-red-4-3","rgb":[226,49,137]},{"group":"vega-purple-red-4","name":"vega-purple-red-4-4","rgb":[198,17,89]}]};

// Polyfills methods that aren't available in Illustrator.
polyfill();

// Document configuration.
var docColorSpace = 'cmyk' === config.document.mode ? DocumentColorSpace.CMYK : DocumentColorSpace.RGB;
var docHeight = mmToPt(config.document.height);
var docWidth = mmToPt(config.document.width);

// Swatch rectangle configuration.
var swatchRectWidth = docWidth / getColorGroups(config.colors).length;
var swatchRectHeight = docHeight / getMaxShades(config.colors);

// Creates a document template.
var docPreset = new DocumentPreset;
docPreset.colorMode = docColorSpace;
docPreset.height = docHeight;
docPreset.width = docWidth;
docPreset.units = RulerUnits.Millimeters;

// Creates a new document.
var doc = app.documents.addDocument(docColorSpace, docPreset);

// Creates character styles.
var charStyles = {};
config.characterStyles.forEach(function (style) {
  var styleAttributes = style.attributes;
  var characterStyle = doc.characterStyles.add(style.name);
  var characterAttributes = characterStyle.characterAttributes;

  Object.keys(styleAttributes).forEach(function (attribute) {
    characterAttributes[attribute] = styleAttributes[attribute];
  });

  charStyles[style.name] = characterStyle;
});

// Removes default swatches and swatch groups created by Illustrator.
removeAllSwatchGroups();
removeAllSwatches();

// Creates and adds swatch groups and swatches.
build(config.colors, config.document.mode);

/**
 * Creates and adds swatch groups and swatches.
 *
 * @param   {Array} colors
 * @param   {String} mode
 */
function build(colors, mode) {
  var colorGroups = getColorGroups(colors);

  colorGroups.forEach(function (colorGroup, colorGroupIndex) {
    // Creates and adds swatch group.
    var swatchGroup = addSwatchGroup(colorGroup);

    // Gets colors that belong to group.
    var groupColors = colors.filter(function (o) {
      return o.group === colorGroup;
    });

    groupColors.forEach(function (groupColor, groupColorIndex) {
      // Creates RGB color.
      var rgb = new RGBColor();
      rgb.red = groupColor.rgb[0];
      rgb.green = groupColor.rgb[1];
      rgb.blue = groupColor.rgb[2];

      var swatchColor = 'cmyk' === mode ? colorToCMYK(rgb) : rgb;

      // Creates and adds swatch to document.
      var swatch = addSwatch(groupColor.name, swatchColor);

      // Adds swatch to swatch group.
      swatchGroup.addSwatch(swatch);

      // Draws rectangle on artboard.
      drawSwatchRect(docHeight - groupColorIndex * swatchRectHeight, colorGroupIndex * swatchRectWidth, swatchRectWidth, swatchRectHeight, groupColor.name, swatchColor);
    });
  });
}

/**
 * Adds swatch group.
 *
 * @param   {String} name
 * @returns {SwatchGroup}
 */
function addSwatchGroup(name) {
  var swatchGroup = doc.swatchGroups.add();
  swatchGroup.name = name;

  return swatchGroup;
}

/**
 * Adds swatch.
 *
 * @param   {String} name
 * @param   {Color} color
 * @returns {Swatch}
 */
function addSwatch(name, color) {
  var swatch = doc.swatches.add();
  swatch.color = color;
  swatch.name = name;

  return swatch;
}

/**
 * Removes all swatches.
 */
function removeAllSwatches() {
  for (var i = 0; i < doc.swatches.length; i++) {
    doc.swatches[i].remove();
  }
}

/**
 * Removes all swatch groups.
 */
function removeAllSwatchGroups() {
  for (var i = 0; i < doc.swatchGroups.length; i++) {
    doc.swatchGroups[i].remove();
  }
}

/**
 * Draws rectangle on artboard.
 *
 * @param   {Number} top
 * @param   {Number} left
 * @param   {Number} width
 * @param   {Number} height
 * @param   {String} name
 * @param   {Color} color
 * @returns {PathItem}
 */
function drawSwatchRect(top, left, width, height, name, color) {
  var layer = doc.layers[0];

  var rect = layer.pathItems.rectangle(top, left, width, height);
  rect.filled = true;
  rect.fillColor = color;
  rect.stroked = false;

  var textBounds = layer.pathItems.rectangle(top - height * config.swatchRect.textPosition, left + width * config.swatchRect.textPosition, width * (1 - config.swatchRect.textPosition * 2), height * (1 - config.swatchRect.textPosition * 2));
  var text = layer.textFrames.areaText(textBounds);
  text.contents = name + '\n' + colorToString(color);

  charStyles['swatchRectTitle'].applyTo(text.textRange);

  return rect;
}

/**
 * Returns an array of unique group names.
 *
 * @param   {Array} colors
 * @returns {Array)
 */
function getColorGroups(colors) {
  var colorGroups = [];

  colors.forEach(function (color) {
    if (colorGroups.indexOf(color.group) < 0) {
      colorGroups.push(color.group);
    }
  });

  return colorGroups;
}

/**
 * Returns maximum number of shades.
 *
 * @param   {Array} colors
 * @returns {Number}
 */
function getMaxShades(colors) {
  var max = 0;
  var colorGroups = getColorGroups(colors);

  colorGroups.forEach(function (colorGroup, colorGroupIndex) {
    // Gets colors that belong to group.
    var groupColors = colors.filter(function (o) {
      return o.group === colorGroup;
    });

    var len = groupColors.length;

    if (len > max) {
      max = len;
    }
  });

  return max;
}

/**
 *
 * @see https://github.com/totorototo/adobe_cc_extension/blob/master/Apps/Panels/src/cep/application/ilst/color.jsx
 * @param   {Color} color
 * @returns {CMYKColor}
 */
function colorToCMYK(color) {
  var cmykColor = new CMYKColor();
  var colors;

  switch (color.typename) {
  case 'CMYKColor':
    cmykColor = color;
    break;

  case 'RGBColor':
    colors = app.convertSampleColor(ImageColorSpace.RGB, [color.red, color.green, color.blue], ImageColorSpace.CMYK, ColorConvertPurpose.dummypurpose);
    cmykColor.cyan = colors[0];
    cmykColor.magenta = colors[1];
    cmykColor.yellow = colors[2];
    cmykColor.black = colors[3];
    break;

  case 'LabColor':
    colors = app.convertSampleColor(ImageColorSpace.LAB, [color.l, color.a, color.b], ImageColorSpace.CMYK, ColorConvertPurpose.dummypurpose);
    cmykColor.cyan = colors[0];
    cmykColor.magenta = colors[1];
    cmykColor.yellow = colors[2];
    cmykColor.black = colors[3];
    break;

  case 'GrayColor':
    colors = app.convertSampleColor(ImageColorSpace.GrayScale, [color.gray], ImageColorSpace.CMYK, ColorConvertPurpose.dummypurpose);
    cmykColor.cyan = colors[0];
    cmykColor.magenta = colors[1];
    cmykColor.yellow = colors[2];
    cmykColor.black = colors[3];
    break;

  case 'SpotColor':
    return colorToCMYK(color.spot.color);
  }

  return cmykColor;
};

/**
 *
 * @param   {Color} color
 * @returns {String}
 */
function colorToString(color) {
  if ('CMYKColor' === color.typename) {
    return [
      Math.round(color.cyan) + '%',
      Math.round(color.magenta) + '%',
      Math.round(color.yellow) + '%',
      Math.round(color.black) + '%'
    ].join(', ');
  }
  else if ('RGBColor' === color.typename) {
    return [
      Math.round(color.red),
      Math.round(color.green),
      Math.round(color.blue)
    ].join(', ');
  }

  return '';
}

/**
 *
 * @param   {Number} mm
 * @returns {Number}
 */
function mmToPt(mm) {
  return mm * 2.834645;
}

/**
 *
 * @param   {Number} pt
 * @returns {Number}
 */
function ptToMm(pt) {
  return pt / 2.834645;
}

/**
 * Polyfills methods that aren't available in Illustrator.
 */
function polyfill() {
  // https://developer.mozilla.org/en/docs/Web/JavaScript/Reference/Global_Objects/Array/filter#Polyfill
  if (!Array.prototype.filter) {
    Array.prototype.filter = function (fun /*, thisArg*/ ) {
      'use strict';

      if (this === void 0 || this === null) {
        throw new TypeError();
      }

      var t = Object(this);
      var len = t.length >>> 0;
      if (typeof fun !== 'function') {
        throw new TypeError();
      }

      var res = [];
      var thisArg = arguments.length >= 2 ? arguments[1] : void 0;
      for (var i = 0; i < len; i++) {
        if (i in t) {
          var val = t[i];

          // NOTE: Technically this should Object.defineProperty at
          //       the next index, as push can be affected by
          //       properties on Object.prototype and Array.prototype.
          //       But that method's new, and collisions should be
          //       rare, so use the more-compatible alternative.
          if (fun.call(thisArg, val, i, t)) {
            res.push(val);
          }
        }
      }

      return res;
    };
  }

  // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/forEach#Polyfill
  if (!Array.prototype.forEach) {
    Array.prototype.forEach = function (callback /*, thisArg*/ ) {

      var T, k;

      if (this == null) {
        throw new TypeError('this is null or not defined');
      }

      // 1. Let O be the result of calling toObject() passing the
      // |this| value as the argument.
      var O = Object(this);

      // 2. Let lenValue be the result of calling the Get() internal
      // method of O with the argument "length".
      // 3. Let len be toUint32(lenValue).
      var len = O.length >>> 0;

      // 4. If isCallable(callback) is false, throw a TypeError exception.
      // See: http://es5.github.com/#x9.11
      if (typeof callback !== 'function') {
        throw new TypeError(callback + ' is not a function');
      }

      // 5. If thisArg was supplied, let T be thisArg; else let
      // T be undefined.
      if (arguments.length > 1) {
        T = arguments[1];
      }

      // 6. Let k be 0
      k = 0;

      // 7. Repeat, while k < len
      while (k < len) {

        var kValue;

        // a. Let Pk be ToString(k).
        //    This is implicit for LHS operands of the in operator
        // b. Let kPresent be the result of calling the HasProperty
        //    internal method of O with argument Pk.
        //    This step can be combined with c
        // c. If kPresent is true, then
        if (k in O) {

          // i. Let kValue be the result of calling the Get internal
          // method of O with argument Pk.
          kValue = O[k];

          // ii. Call the Call internal method of callback with T as
          // the this value and argument list containing kValue, k, and O.
          callback.call(T, kValue, k, O);
        }
        // d. Increase k by 1.
        k++;
      }
      // 8. return undefined
    };
  }

  // https://developer.mozilla.org/en/docs/Web/JavaScript/Reference/Global_Objects/Array/indexOf#Polyfill
  if (!Array.prototype.indexOf) {
    Array.prototype.indexOf = function (searchElement, fromIndex) {
      var k;

      // 1. Let o be the result of calling ToObject passing
      //    the this value as the argument.
      if (this == null) {
        throw new TypeError('"this" is null or not defined');
      }

      var o = Object(this);

      // 2. Let lenValue be the result of calling the Get
      //    internal method of o with the argument "length".
      // 3. Let len be ToUint32(lenValue).
      var len = o.length >>> 0;

      // 4. If len is 0, return -1.
      if (len === 0) {
        return -1;
      }

      // 5. If argument fromIndex was passed let n be
      //    ToInteger(fromIndex); else let n be 0.
      var n = fromIndex | 0;

      // 6. If n >= len, return -1.
      if (n >= len) {
        return -1;
      }

      // 7. If n >= 0, then Let k be n.
      // 8. Else, n<0, Let k be len - abs(n).
      //    If k is less than 0, then let k be 0.
      k = Math.max(n >= 0 ? n : len - Math.abs(n), 0);

      // 9. Repeat, while k < len
      while (k < len) {
        // a. Let Pk be ToString(k).
        //   This is implicit for LHS operands of the in operator
        // b. Let kPresent be the result of calling the
        //    HasProperty internal method of o with argument Pk.
        //   This step can be combined with c
        // c. If kPresent is true, then
        //    i.  Let elementK be the result of calling the Get
        //        internal method of o with the argument ToString(k).
        //   ii.  Let same be the result of applying the
        //        Strict Equality Comparison Algorithm to
        //        searchElement and elementK.
        //  iii.  If same is true, return k.
        if (k in o && o[k] === searchElement) {
          return k;
        }
        k++;
      }

      return -1;
    };
  }

  // https://developer.mozilla.org/en/docs/Web/JavaScript/Reference/Global_Objects/Object/keys#Polyfill
  if (!Object.keys) {
    Object.keys = (function () {
      'use strict';
      var hasOwnProperty = Object.prototype.hasOwnProperty,
        hasDontEnumBug = !({
          toString: null
        }).propertyIsEnumerable('toString'),
        dontEnums = [
          'toString',
          'toLocaleString',
          'valueOf',
          'hasOwnProperty',
          'isPrototypeOf',
          'propertyIsEnumerable',
          'constructor'
        ],
        dontEnumsLength = dontEnums.length;

      return function (obj) {
        if (typeof obj !== 'function' && (typeof obj !== 'object' || obj === null)) {
          throw new TypeError('Object.keys called on non-object');
        }

        var result = [],
          prop, i;

        for (prop in obj) {
          if (hasOwnProperty.call(obj, prop)) {
            result.push(prop);
          }
        }

        if (hasDontEnumBug) {
          for (i = 0; i < dontEnumsLength; i++) {
            if (hasOwnProperty.call(obj, dontEnums[i])) {
              result.push(dontEnums[i]);
            }
          }
        }
        return result;
      };
    }());
  }
}
