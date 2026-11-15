import { useEffect, useRef } from 'react'

// Fond de l'accueil : des courbes de marché qui dérivent lentement. Pur canvas, aucun fichier vidéo.
// Les courbes sont décoratives (sinusoïdes), pas des données : aucun chiffre n'en est tiré.
const COURBES = [
  { base: 0.62, pente: -0.2, a: [0.07, 0.03, 0.012], f: [1.6, 4.1, 11], v: [0.22, -0.5, 0.9], p: [0, 1.2, 0.4], alpha: 0.7, ep: 2.2 },
  { base: 0.7, pente: -0.14, a: [0.06, 0.025, 0.01], f: [1.9, 5.2, 12], v: [0.18, -0.42, 0.8], p: [1.7, 0.3, 2.1], alpha: 0.3, ep: 1.6 },
  { base: 0.5, pente: -0.18, a: [0.08, 0.03, 0.012], f: [1.3, 3.7, 9], v: [0.16, -0.38, 0.7], p: [3.1, 2.2, 1.1], alpha: 0.22, ep: 1.4 },
  { base: 0.78, pente: -0.08, a: [0.05, 0.02, 0.008], f: [2.2, 6, 14], v: [0.26, -0.55, 1], p: [2.4, 0.9, 3], alpha: 0.2, ep: 1.2, encre: true },
  { base: 0.42, pente: -0.1, a: [0.05, 0.02, 0.008], f: [1.1, 3, 10], v: [0.14, -0.33, 0.6], p: [0.8, 1.9, 0.2], alpha: 0.16, ep: 1.2, encre: true },
]

function rgb(couleur, secours) {
  const m = /^#?([0-9a-f]{6})$/i.exec((couleur || '').trim())
  if (!m) return secours
  const n = parseInt(m[1], 16)
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255]
}

export default function FondAnime({ className }) {
  const ref = useRef(null)

  useEffect(() => {
    const cv = ref.current
    const ctx = cv?.getContext('2d')
    if (!cv || !ctx) return
    const style = getComputedStyle(document.documentElement)
    const accent = rgb(style.getPropertyValue('--logo-b'), [106, 38, 238])
    const encre = rgb(style.getPropertyValue('--foreground'), [24, 24, 27])
    const reduit = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    let w = 0, h = 0, raf = 0

    const redimensionner = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2)
      w = cv.clientWidth
      h = cv.clientHeight
      cv.width = Math.round(w * dpr)
      cv.height = Math.round(h * dpr)
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    }
    const yA = (c, x, t) => {
      const u = x / w
      let v = c.base + c.pente * u
      for (let i = 0; i < 3; i++) v += c.a[i] * Math.sin(u * c.f[i] * Math.PI * 2 + t * c.v[i] + c.p[i])
      return v * h
    }
    const trace = (c, t) => {
      ctx.beginPath()
      for (let x = 0; x <= w + 4; x += 4) {
        const y = yA(c, x, t)
        if (x === 0) ctx.moveTo(x, y)
        else ctx.lineTo(x, y)
      }
    }
    const dessiner = (ms) => {
      const t = ms / 1000
      ctx.clearRect(0, 0, w, h)
      ctx.strokeStyle = `rgba(${encre[0]},${encre[1]},${encre[2]},0.05)`
      ctx.lineWidth = 1
      for (let y = 60; y < h; y += 72) { ctx.beginPath(); ctx.moveTo(0, y + 0.5); ctx.lineTo(w, y + 0.5); ctx.stroke() }
      const pas = 96
      for (let x = -((t * 10) % pas); x < w; x += pas) { ctx.beginPath(); ctx.moveTo(x + 0.5, 0); ctx.lineTo(x + 0.5, h); ctx.stroke() }

      COURBES.forEach((c, i) => {
        const col = c.encre ? encre : accent
        if (i === 0) {
          trace(c, t)
          ctx.lineTo(w, h); ctx.lineTo(0, h); ctx.closePath()
          const g = ctx.createLinearGradient(0, h * 0.35, 0, h)
          g.addColorStop(0, `rgba(${col[0]},${col[1]},${col[2]},0.10)`)
          g.addColorStop(1, `rgba(${col[0]},${col[1]},${col[2]},0)`)
          ctx.fillStyle = g
          ctx.fill()
        }
        trace(c, t)
        ctx.strokeStyle = `rgba(${col[0]},${col[1]},${col[2]},${c.alpha})`
        ctx.lineWidth = c.ep
        ctx.lineJoin = 'round'
        ctx.stroke()
      })

      // Un point qui suit la courbe principale.
      const xm = ((((t * 70) % (w + 120)) + (w + 120)) % (w + 120)) - 60
      if (xm > 0 && xm < w) {
        const ym = yA(COURBES[0], xm, t)
        const pouls = (t * 1.2) % 1
        ctx.beginPath(); ctx.arc(xm, ym, 5 + pouls * 14, 0, Math.PI * 2)
        ctx.strokeStyle = `rgba(${accent[0]},${accent[1]},${accent[2]},${0.35 * (1 - pouls)})`
        ctx.lineWidth = 1.5; ctx.stroke()
        ctx.beginPath(); ctx.arc(xm, ym, 4.5, 0, Math.PI * 2)
        ctx.fillStyle = `rgb(${accent[0]},${accent[1]},${accent[2]})`; ctx.fill()
      }
    }
    const boucle = (ms) => { dessiner(ms); raf = requestAnimationFrame(boucle) }

    redimensionner()
    window.addEventListener('resize', redimensionner)
    if (reduit) dessiner(4000)
    else raf = requestAnimationFrame(boucle)
    return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', redimensionner) }
  }, [])

  return <canvas ref={ref} className={className} aria-hidden="true" />
}
