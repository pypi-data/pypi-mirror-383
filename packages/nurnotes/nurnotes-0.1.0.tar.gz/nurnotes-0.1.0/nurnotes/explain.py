# -*- coding: utf-8 -*-

EXPLAINS = {
    "Dünya bir misafirhanedir": "Bu dünya müvəqqəti bir yerdir, insan buraya qonaq kimi gəlir, əsas məqsəd axirətə hazırlıqdır.",
    "İman nuru": "İman insanın qəlbini işıqlandırır, doğru yolu göstərir.",
    "Sabır dərmanıdır": "Sınaqlar qarşısında sabırlı olmaq insanın ruhunu gücləndirir."
}

def explain_sentence(sentence):
    return EXPLAINS.get(sentence, "Bu cümlənin izahı hələ əlavə edilməyib.")

