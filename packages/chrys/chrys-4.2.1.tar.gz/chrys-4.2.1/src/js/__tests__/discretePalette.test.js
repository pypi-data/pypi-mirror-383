import {describe, expect, test} from 'vitest';
import {discretePalette, VEGA_ACCENT} from '..';

describe('discretePalette', () => {
  test('Should generate a palette with 6 colors if size not given', () => {
    expect(discretePalette(VEGA_ACCENT)).toEqual([
      '#7fc97f',
      '#beaed4',
      '#fdc086',
      '#ffff99',
      '#386cb0',
      '#f0027f'
    ]);
  });

  test('Should generate a palette if size given', () => {
    expect(discretePalette(VEGA_ACCENT, 8)).toEqual([
      '#7fc97f',
      '#beaed4',
      '#fdc086',
      '#ffff99',
      '#386cb0',
      '#f0027f',
      '#bf5b17',
      '#666666'
    ]);
  });

  test('Should generate a palette with the maximum number of colors that the palette supports if the given size is larger', () => {
    expect(discretePalette(VEGA_ACCENT, 20)).toEqual([
      '#7fc97f',
      '#beaed4',
      '#fdc086',
      '#ffff99',
      '#386cb0',
      '#f0027f',
      '#bf5b17',
      '#666666'
    ]);
  });

  test('Should throw an error for an invalid palette name', () => {
    expect(() => discretePalette('lorem ipsum')).toThrowError(
      'Palette name "lorem ipsum" not recognized'
    );
  });
});
