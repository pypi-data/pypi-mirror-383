from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

@implementer(IVocabularyFactory)
class IconTypeVocabulary:
    def __call__(self, context):
        terms = [
            SimpleTerm(value=f'aioa-icon-type-{i}', title=f'aioa-icon-type-{i}')
            for i in range(1, 30)
        ]
        return SimpleVocabulary(terms)
    




