"use strict";

(function () {
  var sidebarStorageKey = "academorPortal.sidebarMini";
  var desktopMedia = "(min-width: 992px)";

  function onReady(callback) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", callback);
      return;
    }

    callback();
  }

  function isDesktop() {
    return window.matchMedia(desktopMedia).matches;
  }

  function canUseStorage() {
    try {
      var testKey = sidebarStorageKey + ".test";
      window.localStorage.setItem(testKey, "1");
      window.localStorage.removeItem(testKey);
      return true;
    } catch (error) {
      return false;
    }
  }

  function getSavedMiniState(storageAvailable) {
    if (!storageAvailable) {
      return false;
    }

    return window.localStorage.getItem(sidebarStorageKey) === "true";
  }

  function saveMiniState(storageAvailable, isMini) {
    if (storageAvailable) {
      window.localStorage.setItem(sidebarStorageKey, String(isMini));
    }
  }

  onReady(function () {
    var body = document.body;
    var sidebarToggle = document.querySelector("[data-sidebar-toggle]");
    var closeButtons = document.querySelectorAll("[data-sidebar-close]");
    var mediaQuery = window.matchMedia(desktopMedia);
    var storageAvailable = canUseStorage();

    function initValidation() {
      var forms = document.querySelectorAll(".needs-validation:not([data-portal-bound])");

      Array.prototype.forEach.call(forms, function (form) {
        form.setAttribute("data-portal-bound", "true");
        form.addEventListener("submit", function (event) {
          if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
          }

          form.classList.add("was-validated");
        });
      });
    }

    function initTableSearch() {
      var searchInputs = document.querySelectorAll("[data-table-search]:not([data-portal-bound])");

      Array.prototype.forEach.call(searchInputs, function (input) {
        input.setAttribute("data-portal-bound", "true");
        var tableId = input.getAttribute("data-table-search");
        var table = document.getElementById(tableId);

        if (!table) {
          return;
        }

        var searchTimer = null;
        input.addEventListener("input", function () {
          if (searchTimer) {
            window.clearTimeout(searchTimer);
          }
          searchTimer = window.setTimeout(function () {
            var query = input.value.trim().toLowerCase();
            var rows = table.querySelectorAll("tbody tr");

            Array.prototype.forEach.call(rows, function (row) {
              row.hidden = query !== "" && row.textContent.toLowerCase().indexOf(query) === -1;
            });
          }, 150);
        });
      });
    }

    function getPortalLang() {
      var lang = (document.documentElement.lang || "az").toLowerCase().split("-")[0];
      return lang === "en" || lang === "ru" ? lang : "az";
    }

    function capitalizeWord(value) {
      if (!value) {
        return value;
      }

      return value.charAt(0).toUpperCase() + value.slice(1);
    }

    function formatPortalDate(date, lang) {
      var locale = lang || getPortalLang();
      var monthNames = {
        az: ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul", "avqust", "sentyabr", "oktyabr", "noyabr", "dekabr"],
        en: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        ru: ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"],
      };
      var weekdayNames = {
        az: ["Bazar", "Bazar ertəsi", "Çərşənbə axşamı", "Çərşənbə", "Cümə axşamı", "Cümə", "Şənbə"],
        en: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        ru: ["воскресенье", "понедельник", "вторник", "среда", "четверг", "пятница", "суббота"],
      };
      var months = monthNames[locale] || monthNames.az;
      var weekdays = weekdayNames[locale] || weekdayNames.az;
      var day = date.getDate();
      var month = capitalizeWord(months[date.getMonth()]);
      var year = date.getFullYear();
      var weekday = weekdays[date.getDay()];

      if (locale === "ru") {
        return day + " " + month + " " + year + ", " + capitalizeWord(weekday);
      }

      return day + " " + month + " " + year + ", " + weekday;
    }

    function initPortalDateBadges() {
      var targets = document.querySelectorAll("#current-date, [data-portal-current-date]");

      Array.prototype.forEach.call(targets, function (element) {
        element.textContent = formatPortalDate(new Date(), getPortalLang());
      });
    }

    function initPickerInputs() {
      var inputs = document.querySelectorAll(
        'input[type="date"].form-control, input[type="date"][class*="form-control"], ' +
        'input[type="time"].form-control, input[type="time"][class*="form-control"]'
      );

      Array.prototype.forEach.call(inputs, function (input) {
        if (input.dataset.portalPickerBound) {
          return;
        }
        input.dataset.portalPickerBound = "true";
        input.classList.add("portal-picker-input");
        input.style.cursor = "pointer";

        input.addEventListener("click", function () {
          if (typeof input.showPicker === "function") {
            try {
              input.showPicker();
            } catch (error) {
              input.focus();
            }
          } else {
            input.focus();
          }
        });
      });
    }

    function initProfilePhotoUploader() {
      var form = document.querySelector(".portal-profile-form");
      var input = document.getElementById("id_profile_image");
      var preview = document.getElementById("profilePhotoPreview");
      var previewInitials = document.getElementById("profilePhotoPreviewInitials");
      var removeButton = document.querySelector("[data-profile-photo-remove]");
      var clearCheckbox = document.getElementById("profile_image-clear_id");

      if (!form || !input || form.dataset.portalPhotoBound) {
        return;
      }

      form.dataset.portalPhotoBound = "true";

      input.addEventListener("change", function () {
        if (!input.files || !input.files[0]) {
          return;
        }

        if (preview) {
          preview.src = URL.createObjectURL(input.files[0]);
          preview.classList.remove("d-none");
        }

        if (previewInitials) {
          previewInitials.classList.add("d-none");
        }

        form.submit();
      });

      if (removeButton && clearCheckbox) {
        removeButton.addEventListener("click", function () {
          clearCheckbox.checked = true;
          form.submit();
        });
      }
    }

    function initPageContent() {
      initValidation();
      initTableSearch();
      initPortalDateBadges();
      initPickerInputs();
      initProfilePhotoUploader();
    }

    initPageContent();

    window.AcademorPortal = window.AcademorPortal || {};
    window.AcademorPortal.initPageContent = initPageContent;
    window.AcademorPortal.isDesktop = isDesktop;

    if (!sidebarToggle) {
      return;
    }

    function setClass(element, className, enabled) {
      if (enabled) {
        element.classList.add(className);
      } else {
        element.classList.remove(className);
      }
    }

    function setToggleExpanded() {
      var expanded = isDesktop()
        ? !body.classList.contains("sidebar-mini")
        : body.classList.contains("sidebar-open");

      sidebarToggle.setAttribute("aria-expanded", String(expanded));
    }

    function closeMobileSidebar() {
      body.classList.remove("sidebar-open");
      setToggleExpanded();
    }

    window.AcademorPortal.closeMobileSidebar = closeMobileSidebar;

    function toggleSidebar() {
      if (isDesktop()) {
        body.classList.toggle("sidebar-mini");
        saveMiniState(storageAvailable, body.classList.contains("sidebar-mini"));
      } else {
        body.classList.toggle("sidebar-open");
      }

      setToggleExpanded();
    }

    function addCloseHandlers(items) {
      Array.prototype.forEach.call(items, function (item) {
        item.addEventListener("click", function () {
          if (!isDesktop()) {
            closeMobileSidebar();
          }
        });
      });
    }

    if (getSavedMiniState(storageAvailable) && isDesktop()) {
      body.classList.add("sidebar-mini");
    }

    sidebarToggle.addEventListener("click", toggleSidebar);
    addCloseHandlers(closeButtons);

    body.addEventListener("click", function (event) {
      var link = event.target.closest("#adminSidebar .sidebar-nav .nav-link");
      if (link && !isDesktop()) {
        closeMobileSidebar();
      }
    });

    setToggleExpanded();

    function handleBreakpointChange() {
      if (isDesktop()) {
        body.classList.remove("sidebar-open");
        setClass(body, "sidebar-mini", getSavedMiniState(storageAvailable));
      } else {
        body.classList.remove("sidebar-mini");
      }

      setToggleExpanded();
    }

    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener("change", handleBreakpointChange);
    } else if (mediaQuery.addListener) {
      mediaQuery.addListener(handleBreakpointChange);
    }
  });
})();
