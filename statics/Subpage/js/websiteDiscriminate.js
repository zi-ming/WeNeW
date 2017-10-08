var locked_tag = null;


function hoverHandler(ths) {
    /*
    * 鼠标掠过标签事件
    * */
    var islocked = int2Bool(ths, "islocked");
    var activated = int2Bool(ths, "activated");
    reverseBoolean(ths, "activated");
    if(islocked == false) {
        changeTagStyle(ths, "activated");
    }
}


function lockTag(ths) {
    /*
    * 锁定标签
    * */
    var islocked = int2Bool(ths, "islocked");
    if(islocked){       // 原本已经Locked，现在取消Locked
        locked_tag = null;
    }else{
        if(locked_tag!=null){
            reverseBoolean(locked_tag, "islocked");
            changeTagStyle(locked_tag, "islocked");
        }
        locked_tag = ths;
    }
    reverseBoolean(ths, "islocked");
    changeTagStyle(ths, "islocked");
}


function clickHandler(ths) {
    /*
    * 鼠标点击标签事件
    * */
    lockTag(ths);
}


function init_link_tag(tag, index) {
    /*
    * 初始化所有链接标签
    * */
    var nodes = tag.children;
    for(var i=0; i<nodes.length; i++){
        init_link_tag(nodes[i], index + 1 + i);
    }
    if(tag.tagName.toLowerCase()!="link" && (tag.getAttribute("href") || tag.getAttribute("hrefs"))){
        tag.setAttribute("tag_id", index);
        tag.setAttribute("islocked", 0);
        tag.setAttribute("activated", 0);
        tag.setAttribute("onmouseover", "hoverHandler(this);event.cancelBubble = true;");
        tag.setAttribute("onmouseout", "hoverHandler(this);event.cancelBubble = true;");
        tag.setAttribute("onclick", "clickHandler(this);event.cancelBubble = true;");

        var style = new Array();
        style['background-color'] = tag.style.backgroundColor;
        style["opacity"] = tag.style.opacity;
        originalStyle[index] = style;
    }
}


function submit() {
    /*
    * 保存网站的xpath
    * */
    var res = document.evaluate("//*[@islocked='1']", document, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null);
    if(res.snapshotLength > 0){
        node = res.snapshotItem(0);
        var xpath = formAbsXpath(node);
        var sub_info = document.getElementById("sub_info");
        var website_url = sub_info.getAttribute("website_url");
        var detail = sub_info.getAttribute("detail");
        var content_url = node.getAttribute("href") || node.getAttribute("hrefs");
        if(sub_info.getAttribute("content_url").length > 0){
            content_url = sub_info.getAttribute("content_url");
        }
        var success = function () {
            website_url = argsEncode(website_url); // 加工处理
            content_url = argsEncode(content_url); // 加工处理
            window.location.href = "/sub/contentSub/?website_url="+website_url+"&content_url="+content_url;
        };
        Ajax.post("/sub/saveWebsiteXpath",{"website_url":website_url,
            "detail":detail,"xpath": xpath}, success); // 保存菜单xpath， 且打开链接内容页，进行内容xpath筛选
    }
}


function addWebsiteToolDiv() {
    /*
    * 添加订阅工具
    * */
    sub_tool = "<div class='sub_container'>" +
        "<div class='sub_button_m active' onclick='submit();'>提交</div>"+
        "</div>";
    document.body.innerHTML+=sub_tool;
}

window.onload = function () {
    hrefHandler();
    imgSrcHandler();
    init_link_tag(document.body, 0);
    addWebsiteToolDiv();
    prevent_tag_Click(document.body);
};