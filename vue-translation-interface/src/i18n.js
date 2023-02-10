import { createI18n } from 'vue-i18n'
import eo from './lang/eo';
import fr from './lang/fr';
import en from './lang/en';
import pl from './lang/pl';
import fi from './lang/fi';
import it from './lang/it';
import pt from './lang/pt';
import ms from './lang/ms';
import cs from './lang/cs';
import nl from './lang/nl';
import sk from './lang/sk';
import ca from './lang/ca';

const currentLocale =  window.vueTranslationInterface.currentLocale;

const messages = {
    eo,
    fr,
    en,
    pl,
    fi,
    it,
    pt,
    ms,
    cs,
    nl,
    sk,
    ca
};

function pluralRuleFrench(choice) {
  return choice >= 2 ? 1 : 0;
}

function pluralRulePolish(n) {
  return n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2;
}

function pluralRuleSlovak(n) {
  return n==1 ? 0 : (n>=2 && n<=4) ? 1 : 2;
}

const i18n = createI18n({
    locale: currentLocale,
    fallbackLocale: 'eo',
    messages,
    pluralizationRules: {
      fr: pluralRuleFrench,
      pl: pluralRulePolish,
      sk: pluralRuleSlovak,
      cs: pluralRuleSlovak,
    }
});

export default i18n;