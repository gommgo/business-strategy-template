// svgo 4.1.0: preset-default, но подпись Recraft сохраняется. Одного removeMetadata:false мало — неизвестный элемент
// <recraft-signature> удаляет removeUnknownsAndDefaults (unknownContent), его тоже выключаем.
export default { multipass: true, floatPrecision: 1,
  plugins: [{ name: 'preset-default', params: { overrides: { removeMetadata: false,
    removeUnknownsAndDefaults: { unknownContent: false } } } }] };
