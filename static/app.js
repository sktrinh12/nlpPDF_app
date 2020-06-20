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
};

document.querySelector('.custom-file-input').addEventListener('change',function(e){ //show filename in the input
  var fileName = document.getElementById("pdf_up").files[0].name;
  var nextSibling = e.target.nextElementSibling
  nextSibling.innerText = fileName
});
