# logos-chat

Gerador de assets de marca (PNG/ICO) a partir de SVGs. Mantem a mesma nomenclatura j´\ usada no projeto.

## Entradas (SVG)

O script procura os arquivos nesta ordem:

1. `scripts/` (mesma pasta do script)
2. `brand-assets/`

Arquivos esperados:

- `logo_thumbnail.svg` (avatar/contraída) **usado para gerar todos os icones**
- `logo.svg` (extendida clara)
- `logo_dark.svg` (extendida escura)

> As versões extendidas são apenas validadas (não são renderizadas no script).

## Como gerar

```powershell
python -m pip install -r scripts\requirements.txt
python scripts\generate-brand-assets.py
```

Por padrão os arquivos são gerados na raiz do reposit�rio (substituem os atuais).

## Saídas geradas

- Android: `android-icon-36/48/72/96/144/192.png`
- Apple: `apple-icon-57/60/72/76/114/120/144/152/180.png`
- Favicon PNG: `favicon-16/32/96.png`
- Favicon SVG: `favicon.svg` (48x48)
- Favicon ICO: `favicon.ico` (16/32/48)
- Microsoft: `ms-icon-70/144/150.png`

## Opções úteis

```powershell
python scripts\generate-brand-assets.py --out-dir public
python scripts\generate-brand-assets.py --avatar-svg .\minha-logo.svg
python scripts\generate-brand-assets.py --skip-favicon-svg
```

## Manifest

O `manifest.json` referencia os �cones Android gerados acima.
