import assert from 'node:assert/strict'
import test from 'node:test'
import { symbolesPortefeuille } from '../src/portefeuille.js'

test('une liste et un dictionnaire permettent les mêmes opérations sur les symboles', () => {
  const poids = { 'XIU.TO': 0.7, 'XBB.TO': 0.3 }
  const liste = ['XIU.TO', 'XBB.TO']
  for (const entree of [liste, poids]) {
    const symboles = symbolesPortefeuille(entree)
    assert.deepEqual(symboles.map((t) => t), liste)
    assert.equal(symboles.includes('XIU.TO'), true)
    assert.deepEqual(symboles.filter((t) => t !== 'XIU.TO'), ['XBB.TO'])
    symboles.push('TSLA')
  }
  assert.deepEqual(liste, ['XIU.TO', 'XBB.TO'])
  assert.deepEqual(poids, { 'XIU.TO': 0.7, 'XBB.TO': 0.3 })
  assert.deepEqual(symbolesPortefeuille(null), [])
  assert.deepEqual(symbolesPortefeuille(undefined), [])
})
