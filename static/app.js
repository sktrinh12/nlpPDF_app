function filesize(elem){
  var fz = elem.files[0].size;
  console.log(fz);
  document.cookie = `filesize=${fz}`;
};

function clear_fz(){ //set the filesize back to 0 again
  console.log('clear');
  document.cookie = "filesize=0";
};

function close_btn(){ //close the flash message
  $('#flash-msg').html("");
  clear_fz();
};

document.querySelector('.custom-file-input').addEventListener('change',function(e){ //show filename in the input
  var fileName = document.getElementById("pdf_up").files[0].name;
  var nextSibling = e.target.nextElementSibling
  nextSibling.innerText = fileName
});

// loader appears in between pages and links
window.addEventListener("load", function () {
    const loaderWrap = document.querySelector(".loader-wrapper");
    loaderWrap.className += " hidden";
});

// loader appears after click button and waiting for flask to finish
function loading() {
    document.querySelector(".loader-wrapper").className = "loader-wrapper";
    setTimeout(clear_fz, 12000);
};

// loader appears if refresh button pressed (ctrl or cmd R)
// document.addEventListener("keydown", function onEvent(event) {
//     var f5key = 116;
//     // if (event.key === "r" && event.ctrlKey) {
//     //   console.log('ctrl R pressed');
//     // }
//     // event.metaKey read-only property returning a Boolean that indicates if the 
//     // Meta key was pressed (true) or not (false) when the event occurred
//     if (event.key === "r" && event.keyCode <= 90 || 
//         event.key === "r" && event.ctrlKey ||
//         event.which == f5key) {
//     var char = (event.metaKey ? '⌘-' : '') + String.fromCharCode(event.keyCode)
//     console.log('<kbd>' + char + '</kbd>' + ' refreshing ...');
//     loading();
//   }
// });

// use of onbeforeunload to detect refresh 
function loader_refresh() {
  loading();
  console.log('refresh button clicked');
};
