import chroma from 'chroma-js';

const ALGORITHM = {
  APCA: 'apca',
  WCAG: 'wcag'
};

export function bestColorContrast(
  bgColor,
  fgColors,
  algorithm = ALGORITHM.APCA
) {
  let fn;

  if (algorithm === ALGORITHM.APCA) {
    fn = chroma.contrastAPCA;
  } else {
    fn = chroma.contrast;
  }

  const scores = fgColors.map((fgColor) => Math.abs(fn(bgColor, fgColor)));
  const maxScore = Math.max(...scores);
  const maxScoreIndex = scores.indexOf(maxScore);

  return fgColors[maxScoreIndex];
}
