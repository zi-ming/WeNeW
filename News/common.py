def urlEncode(url):
    """
    @summary: url地址解码
    :param url: 源url地址
    :return:    解码后的url地址
    """
    return url.replace("&", "(-)__(-)")