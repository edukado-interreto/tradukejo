import { createI18n } from 'vue-i18n'
import eo from './lang/eo';
import fr from './lang/fr';
import en from './lang/en';

const currentLocale =  window.vueTranslationInterface.currentLocale;

const messages = {
    eo,
    fr,
    en
};

function pluralRuleFrench(choice) {
  return choice >= 2 ? 1 : 0;
}

const i18n = createI18n({
    locale: currentLocale,
    fallbackLocale: 'eo',
    messages,
    pluralizationRules: {
      fr: pluralRuleFrench
    }
});

export default i18n;