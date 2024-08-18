import jieba


def participle_words(text: str, mode="precise") -> set:
    """
    分词函数
    """
    match mode:
        case "precise":
            # 精准模式
            seg_gen = jieba.cut(text, cut_all=False)
        case "full":
            # 全模式
            seg_gen = jieba.cut(text, cut_all=True)
            pass
        case "search_engine":
            # 搜索引擎模式
            seg_gen = jieba.cut_for_search(text)
            pass
        case "news":
            # 新闻模式
            seg_gen = jieba.cut(text)
            pass
    seg_set = set(seg_gen)

    return seg_set


if __name__ == "__main__":
    print(participle_words("你好世界"))
