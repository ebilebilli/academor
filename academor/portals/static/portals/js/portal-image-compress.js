(function () {
  "use strict";

  var FIELD_MAX_DIMENSIONS = {
    profile_image: { width: 400, height: 400 },
    image: { width: 1920, height: 1080 },
    image_files: { width: 1920, height: 1080 },
  };

  var DEFAULT_MAX = { width: 1920, height: 1080 };

  function supportsWebP() {
    try {
      var canvas = document.createElement("canvas");
      canvas.width = 1;
      canvas.height = 1;
      return canvas.toDataURL("image/webp").indexOf("data:image/webp") === 0;
    } catch (error) {
      return false;
    }
  }

  function getMaxDimensions(inputName) {
    if (!inputName) {
      return DEFAULT_MAX;
    }
    return FIELD_MAX_DIMENSIONS[inputName] || DEFAULT_MAX;
  }

  function compressImageToWebP(file, maxWidth, maxHeight, quality) {
    return new Promise(function (resolve, reject) {
      var reader = new FileReader();

      reader.onload = function (event) {
        var img = new Image();

        img.onload = function () {
          var canvas = document.createElement("canvas");
          var width = img.width;
          var height = img.height;

          if (width > maxWidth || height > maxHeight) {
            var ratio = Math.min(maxWidth / width, maxHeight / height);
            width = Math.round(width * ratio);
            height = Math.round(height * ratio);
          }

          canvas.width = width;
          canvas.height = height;

          var ctx = canvas.getContext("2d");
          ctx.drawImage(img, 0, 0, width, height);

          canvas.toBlob(
            function (blob) {
              if (!blob) {
                reject(new Error("WebP conversion failed"));
                return;
              }
              var baseName = file.name.replace(/\.[^/.]+$/, "");
              resolve(
                new File([blob], baseName + ".webp", {
                  type: "image/webp",
                  lastModified: Date.now(),
                })
              );
            },
            "image/webp",
            quality
          );
        };

        img.onerror = function () {
          reject(new Error("Image loading failed"));
        };

        img.src = event.target.result;
      };

      reader.onerror = function () {
        reject(new Error("File reading failed"));
      };

      reader.readAsDataURL(file);
    });
  }

  function isImageFile(file) {
    return file && file.type && file.type.indexOf("image/") === 0;
  }

  function portalCompressImageFiles(files, options) {
    options = options || {};
    if (!supportsWebP()) {
      return Promise.resolve(Array.prototype.slice.call(files || []));
    }

    var list = Array.prototype.slice.call(files || []);
    if (!list.length) {
      return Promise.resolve([]);
    }

    var maxWidth = options.maxWidth || DEFAULT_MAX.width;
    var maxHeight = options.maxHeight || DEFAULT_MAX.height;
    var quality = typeof options.quality === "number" ? options.quality : 0.82;

    return Promise.all(
      list.map(function (file) {
        if (!isImageFile(file)) {
          return file;
        }
        return compressImageToWebP(file, maxWidth, maxHeight, quality).catch(function () {
          return file;
        });
      })
    );
  }

  function portalCompressInputFiles(input, options) {
    if (!input || !input.files || !input.files.length) {
      return Promise.resolve([]);
    }
    var inputName = input.getAttribute("name") || "";
    var dims = getMaxDimensions(inputName);
    var merged = {
      maxWidth: options && options.maxWidth ? options.maxWidth : dims.width,
      maxHeight: options && options.maxHeight ? options.maxHeight : dims.height,
      quality: options && options.quality,
    };
    return portalCompressImageFiles(input.files, merged).then(function (compressed) {
      try {
        var dt = new DataTransfer();
        compressed.forEach(function (file) {
          dt.items.add(file);
        });
        input.files = dt.files;
      } catch (error) {
        /* keep original files */
      }
      return compressed;
    });
  }

  window.portalCompressImageFiles = portalCompressImageFiles;
  window.portalCompressInputFiles = portalCompressInputFiles;
})();
