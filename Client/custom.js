/*
file: custom.js, here add your own custom js code.
 */

// dropdown navbar
var dropdown = document.getElementsByClassName("dropdown-btn");
var i;
var j;
var k;

for (i = 0; i < dropdown.length; i++) {
  dropdown[i].addEventListener("click", function() {
    if (!this.classList.contains("dropdownactive")) clearActive(dropdown);
    this.classList.toggle("dropdownactive");
    var dropdownTabs = this.nextElementSibling;
    if (dropdownTabs.style.display === "block") {
      dropdownTabs.style.display = "none";
    } else {
      dropdownTabs.style.display = "block";
      collapseList(dropdown);
    }
  });
}

function clearActive(dropdown) {
  for (j = 0; j < dropdown.length; j++) {
    if (dropdown[j].classList.contains("dropdownactive")) {
      dropdown[j].classList.remove("dropdownactive");
    }
  }
}

function collapseList(dropdown) {
  for (k = 0; k < dropdown.length; ++k) {
    if (!dropdown[k].classList.contains("dropdownactive")) {
      dropdown[k].nextElementSibling.style.display = "none";
    }
  }
}

//students dropdown
var acc = document.getElementsByClassName("accordion");

for (i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var panel = this.nextElementSibling;
    if (panel.style.maxHeight) {
      panel.style.maxHeight = null;
    } else {
      panel.style.maxHeight = panel.scrollHeight + "px";
    }
  });
}

// tabs
function openPage(pageName, elmnt, color) {
  var tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablink");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].style.backgroundColor = "";
  }
  document.getElementById(pageName).style.display = "block";
  elmnt.style.backgroundColor = color;
}

// default tab open
var defTab = document.getElementsByClassName("defaultOpen");

for (i = 0; i < defTab.length; i++) {
  defTab[i].click();
}

// search bar
var searchBar,
  key = "key=";

// assign value - search page
var posKey = location.href.lastIndexOf(key) + key.length;
if (posKey !== key.length - 1) {
  searchBar = location.href.slice(posKey);
  document.getElementById("search-input").value = searchBar;
  setTimeout(function() {
    document
      .getElementById("search-input")
      .dispatchEvent(new KeyboardEvent("keyup", { key: 13 }));
  }, 100);
}

function search(evt) {
  searchBar = document.getElementById("search-input").value;
  if (evt.keyCode === 13) {
    // redirect to search page
    redirectSearch();
  }
}

function redirectSearch() {
  if (searchBar !== "")
    window.location.href = baseurl + "/search.html?" + key + searchBar;
}

document
  .getElementById("search-input")
  .addEventListener("keydown", search, false);

document
  .getElementById("search-button")
  .addEventListener("click", redirectSearch, false);
