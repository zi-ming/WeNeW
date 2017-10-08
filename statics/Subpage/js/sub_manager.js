
function websiteClickHandler(ths) {
    var pre = ths.previousElementSibling;
    reverseBoolean(ths, "del");
    var del = int2Bool(ths, 'del');
    var id = ths.getAttribute("id");
    if(del){
        pre.setAttribute("class", "website-item website-url-deactive");
        ths.setAttribute("class", "website-item website-reset");
        ths.innerHTML = "&#10226";
    }else{
        pre.setAttribute("class", "website-item website-url-active");
        ths.setAttribute("class", "website-item website-del");
        ths.innerText = "×";
    }
}


function initPage() {
    var nodes = document.getElementsByClassName("website-del");
    for(var i=0; i<nodes.length; i++){
        nodes[i].setAttribute("onclick", "websiteClickHandler(this);");
        setAttrBoolean(nodes[i], "del", false);
    }
}


function submitClickHandler() {
    var website_ids = new Array();
    var items = document.getElementsByClassName("website-reset");
    for(var i=0; i<items.length; i++){
        website_ids.push(items[i].getAttribute("id"))
    }

    var success = function (data) {
      if(data.toString() == "0"){
          alert("保存成功.");
          location.reload();
      }else{
          alert(data);
      }
    };

    Ajax.post("", {"website_ids":JSON.stringify(website_ids)}, success);
}

document.getElementsByClassName("custom-del")[0].setAttribute("onclick","submitClickHandler()");

window.onload = function () {
  initPage();
};