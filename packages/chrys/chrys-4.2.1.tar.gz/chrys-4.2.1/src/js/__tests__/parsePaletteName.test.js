import {describe, expect, test} from 'vitest';
import {parsePaletteName, VEGA_ACCENT} from '..';

describe('parsePaletteName', () => {
  test('Should parse a valid palette name', () => {
    expect(parsePaletteName(VEGA_ACCENT)).toEqual({
      vendor: 'vega',
      palette: 'accent'
    });
  });

  test('Should throw an error for an invalid palette name', () => {
    expect(() => parsePaletteName('lorem ipsum')).toThrowError(
      'Palette name "lorem ipsum" not recognized'
    );
  });
});
