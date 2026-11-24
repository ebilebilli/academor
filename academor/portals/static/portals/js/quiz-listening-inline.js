/* Listening gap-fill (templates/portals/includes/quiz_listening_section.html): like the computer-
   delivered IELTS test, the answer box sits inside the sentence where the blank ("____") is, and shows
   the question number until the student types. Without a blank the box simply follows the prompt.
   Only the input element moves, so names / data attributes and submission stay the same. */
(function () {
  "use strict";

  var BLANK = /_{3,}|…{2,}|\.{4,}/;

  function findBlank(root) {
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    var node = walker.nextNode();
    while (node) {
      var match = BLANK.exec(node.nodeValue);
      if (match) {
        return { node: node, index: match.index, length: match[0].length };
      }
      node = walker.nextNode();
    }
    return null;
  }

  function inlineTask(task) {
    if (task.dataset.listeningInline === "true") {
      return;
    }
    var prompt = task.querySelector("[data-listening-prompt]");
    var input = task.querySelector("input[data-quiz-spr-input]");
    if (!prompt || !input) {
      return;
    }
    task.dataset.listeningInline = "true";
    var number = task.getAttribute("data-quiz-nav-number") || "";
    input.classList.add("portal-listening-gap");
    if (number) {
      input.setAttribute("placeholder", number);
    }
    var blank = findBlank(prompt);
    if (blank) {
      var after = blank.node.splitText(blank.index);
      after.nodeValue = after.nodeValue.slice(blank.length);
      after.parentNode.insertBefore(input, after);
      task.classList.add("is-gap-inline");
    } else {
      var target = prompt.lastElementChild || prompt;
      target.appendChild(document.createTextNode(" "));
      target.appendChild(input);
      task.classList.add("is-gap-after");
    }
  }

  function init(root) {
    (root || document).querySelectorAll(".portal-listening-task--gap").forEach(inlineTask);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { init(); });
  } else {
    init();
  }
  document.addEventListener("portal:content-loaded", function () { init(); });
})();
