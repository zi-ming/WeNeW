function deepCopyXpathResultObj(xpath_result) {
    /*
    * 标签深度复制，用于发布订阅模式下的对象传递，防止源数据被更改
    * :xpath_result: document.evaluate的结果
    * */
    var arr = [];
    for(var i = 0; i<xpath_result.snapshotLength; i++){
        arr.push(xpath_result.snapshotItem(i).cloneNode(true));
    }
    return arr;
}


function formAbsXpath(node) {
    /*
    * 以body为根节点，根据节点名称生成对应的xpath
    * :node: 目标节点
    * */
    var parentNode = node.parentNode,
        xpath = node.tagName.toLowerCase();
    
    while(true){
        if(parentNode && parentNode.tagName.toLowerCase() == "body"){
            return "//" + parentNode.tagName.toLowerCase() + "/" + xpath;
        }

        xpath = parentNode.tagName.toLowerCase() + "/" + xpath;
        currentNode = parentNode;
        parentNode = currentNode.parentNode;
    }
}


function formPythonSingleValueXpath(xpath, node) {
    /*
    * 根据js的xpath形成python格式的xpath
    * :xpath: js格式的xpath值
    * :node: 目标节点
    * */
    var pre_xpath = xpath,
        lat_xpath = "",
        flag = 0,
        tmp_nodes = null,
        tmp_node = null;

    var nodes = document.evaluate(pre_xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
    while(nodes.snapshotLength != 1){
        tmp_node = node.parentNode;
        tmp_nodes = tmp_node.children;
        index = 0;
        for(var i=0; i<tmp_nodes.length; i++){
            if(tmp_nodes[i].tagName.toLowerCase() == node.tagName.toLowerCase()){
                index++;
            }
            if(tmp_nodes[i].outerHTML == node.outerHTML){
                pre_xpath += "["+index+"]";
            }
        }
        node = node.parentNode;

        flag = pre_xpath.lastIndexOf('/');
        lat_xpath = pre_xpath.substring(flag, pre_xpath.length) + lat_xpath;
        pre_xpath = pre_xpath.substring(0, flag);

        nodes = document.evaluate(pre_xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
    }
    return pre_xpath + lat_xpath + "/text()";
}


function formXpath(type) {
    /*
    * 根据节点类型形成xpath， 并发布订阅
    * */
    var xpath = type!="3"? formContent_singleValueType_xpath(type, infos[type]):formContent_multiValueType_xpath(type, infos[type]);
    if(!xpath) {
        parent.PUB.updatePreview(type, "");
        return;
    }
    var obj = document.evaluate(type=="3"?xpath:"//*[@sub_type='"+type+"']/text()", document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
    if(obj) {
        parent.PUB.updatePreview(type, deepCopyXpathResultObj(obj));
        return xpath;
    }else{
        alert("[Fatal Error] formXpath error!\n*please give up current operate and click F5 to reflesh current page.");
        return "";
    }
}


function formContent_singleValueType_xpath(sub_type, info){
    /*
    * 根据单一值的类型形成python格式的xpath
    * */
    var node = document.evaluate("//*[@sub_type='"+sub_type+"']", document, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null);
    if(node.snapshotLength == 0){
        // alert("所选"+info+"为空，请重新检查.");
        return "";
    }else{
        node = node.snapshotItem(0);
        xpath = formAbsXpath(node);
        // 因为document.evaluate的识别规则与python的不一样，所以这里要专门生成python的xpath
        return formPythonSingleValueXpath(xpath, node);
    }
}


function formContent_multiValueType_xpath(sub_type, info){
    /*
    * 根据多选值的类型形成相应的xpath（这里只是js格式的xpath，可能与python不一致，有待测试）
    * */
    var nodes = document.evaluate("//*[@sub_type='"+sub_type+"']", document, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null);
    if(nodes.snapshotLength == 0){
        // alert("所选"+info+"为空，请重新检查.");
        return "";
    }else{
        var xpath = [], tmp_xpath="";
        for(var i=0; i<nodes.snapshotLength; i++){
            tmp_xpath = formAbsXpath(nodes.snapshotItem(i));
            if(!str_in_array(tmp_xpath, xpath))
                xpath.push(tmp_xpath);
        }
        return xpath.join("|");
    }
}