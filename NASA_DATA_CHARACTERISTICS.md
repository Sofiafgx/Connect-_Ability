# 🌟 NASA Exoplanet Data - Повні Характеристики

## Джерела даних NASA з усіма необхідними характеристиками для аналізу екзопланет

---

## 🗄️ **ОСНОВНІ ДЖЕРЕЛА NASA ДАНИХ**

### 1. **NASA Exoplanet Archive**
- **URL**: https://exoplanetarchive.ipac.caltech.edu/
- **Дані**: Підтверджені екзопланети з повними характеристиками
- **Оновлення**: Щоденно
- **Формат**: CSV, JSON, FITS, VOTable

### 2. **TESS (Transiting Exoplanet Survey Satellite)**
- **URL**: https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html
- **Дані**: Lightcurve дані з 2-хвилинним та 20-секундним кадром
- **Покриття**: Майже все небо
- **Період**: 2018 - теперішній час

### 3. **Kepler Space Telescope**
- **URL**: https://archive.stsci.edu/kepler/
- **Дані**: Високоточні lightcurve дані
- **Кадр**: 30 хвилин (довгий), 1 хвилина (короткий)
- **Період**: 2009-2017

### 4. **K2 Mission**
- **URL**: https://archive.stsci.edu/k2/
- **Дані**: Продовження місії Kepler
- **Кампанії**: 19 різних полів спостереження

---

## 📊 **ПОВНІ ХАРАКТЕРИСТИКИ ДОСТУПНІ В NASA ДАНИХ**

### 🌟 **ЗОРЯНІ ВЛАСТИВОСТІ (Stellar Properties)**

| Параметр | Опис | Одиниці | NASA Код |
|----------|------|---------|----------|
| **Ефективна температура** | Температура поверхні зірки | K | `st_teff` |
| **Зоряний радіус** | Радіус зірки | R☉ | `st_rad` |
| **Зоряна маса** | Маса зірки | M☉ | `st_mass` |
| **Металічність** | [Fe/H] відносно Сонця | dex | `st_met` |
| **Поверхнева гравітація** | log g | cm/s² | `st_logg` |
| **Зоряна густина** | Густина зірки | g/cm³ | `st_dens` |
| **Зоряний вік** | Вік зірки | Gyr | `st_age` |
| **V-величина** | Видима зоряна величина | mag | `sy_vmag` |
| **K-величина** | Інфрачервона величина | mag | `sy_kmag` |
| **Gaia величина** | Gaia DR2/DR3 величина | mag | `sy_gaiamag` |

### 🪐 **ПЛАНЕТАРНІ ВЛАСТИВОСТІ (Planetary Properties)**

| Параметр | Опис | Одиниці | NASA Код |
|----------|------|---------|----------|
| **Радіус планети** | Радіус планети | R⊕ | `pl_rade` |
| **Маса планети** | Маса планети | M⊕ | `pl_masse` |
| **Орбітальний період** | Період обертання | дні | `pl_orbper` |
| **Велика піввісь** | Відстань від зірки | AU | `pl_orbsmax` |
| **Ексцентриситет** | Ексцентриситет орбіти | - | `pl_orbeccen` |
| **Нахил орбіти** | Кут нахилу | градуси | `pl_orbincl` |
| **Довгота периастру** | Орієнтація орбіти | градуси | `pl_orblper` |
| **Температура рівноваги** | Розрахункова температура | K | `pl_eqt` |
| **Інсоляція** | Потік випромінювання | S⊕ | `pl_insol` |
| **Густина планети** | Об'ємна густина | g/cm³ | `pl_dens` |

### 🌅 **ТРАНЗИТНІ ВЛАСТИВОСТІ (Transit Properties)**

| Параметр | Опис | Одиниці | NASA Код |
|----------|------|---------|----------|
| **Глибина транзиту** | (Rp/Rs)² | % | `pl_trandep` |
| **Тривалість транзиту** | Повна тривалість | години | `pl_trandur` |
| **Епоха транзиту** | Час середини транзиту | BJD | `pl_tranmid` |
| **Параметр удару** | Відстань від центра диска | Rs | `pl_imppar` |
| **a/Rs** | Відношення орбіти до радіуса | - | `pl_ratdor` |
| **Rp/Rs** | Відношення радіусів | - | `pl_ratror` |
| **Тривалість T14** | Від першого до четвертого контакту | години | `pl_trandurT14` |
| **Тривалість T23** | Від другого до третього контакту | години | `pl_trandurT23` |

### 🔭 **СПОСТЕРЕЖНІ ВЛАСТИВОСТІ (Observational Properties)**

| Параметр | Опис | Одиниці | NASA Код |
|----------|------|---------|----------|
| **Пряме сходження** | RA координата | градуси | `ra` |
| **Схилення** | Dec координата | градуси | `dec` |
| **Відстань** | Відстань до системи | парсеки | `sy_dist` |
| **Власний рух RA** | Рух по RA | mas/рік | `sy_pmra` |
| **Власний рух Dec** | Рух по Dec | mas/рік | `sy_pmdec` |
| **Радіальна швидкість** | Променева швидкість | км/с | `st_radv` |
| **Паралакс** | Тригонометричний паралакс | mas | `sy_plx` |

### 📅 **ІНФОРМАЦІЯ ПРО ВІДКРИТТЯ (Discovery Information)**

| Параметр | Опис | NASA Код |
|----------|------|----------|
| **Рік відкриття** | Рік публікації відкриття | `disc_year` |
| **Метод відкриття** | Спосіб виявлення | `discoverymethod` |
| **Обсерваторія** | Установка відкриття | `disc_facility` |
| **Інструмент** | Конкретний інструмент | `disc_instrument` |
| **Телескоп** | Телескоп відкриття | `disc_telescope` |
| **Посилання** | Наукова публікація | `disc_refname` |

---

## 🛰️ **LIGHTCURVE ДАНІ З МІСІЙ NASA**

### **TESS Lightcurve Характеристики:**

```python
tess_data_structure = {
    'time': 'BJD - 2457000',           # Час у Barycentric Julian Date
    'flux': 'e-/s',                   # Потік у електронах за секунду  
    'flux_err': 'e-/s',               # Похибка потоку
    'quality': 'bitmask',             # Прапорці якості даних
    'cadenceno': 'int',               # Номер кадру
    'centroid_col': 'pixels',         # Центроїд по стовпцях
    'centroid_row': 'pixels',         # Центроїд по рядках
    'sap_flux': 'e-/s',              # Simple Aperture Photometry
    'pdcsap_flux': 'e-/s',           # Pre-search Data Conditioning
    'psf_centr1': 'pixels',          # PSF центроїд 1
    'psf_centr2': 'pixels',          # PSF центроїд 2
    'mom_centr1': 'pixels',          # Moment центроїд 1
    'mom_centr2': 'pixels'           # Moment центроїд 2
}
```

### **Kepler Lightcurve Характеристики:**

```python
kepler_data_structure = {
    'time': 'BJD - 2454833',          # Kepler BJD epoch
    'flux': 'e-/s',                   # Калібрований потік
    'flux_err': 'e-/s',               # Похибка потоку
    'quality': 'bitmask',             # Прапорці якості
    'pos_corr1': 'pixels',            # Корекція позиції 1
    'pos_corr2': 'pixels',            # Корекція позиції 2
    'sap_flux': 'e-/s',              # SAP потік
    'pdcsap_flux': 'e-/s',           # PDC потік
    'sap_bkg': 'e-/s',               # Фон SAP
    'pdcsap_flux_err': 'e-/s'        # Похибка PDC потоку
}
```

---

## 🔍 **ПРИКЛАДИ SQL ЗАПИТІВ ДО NASA ARCHIVE**

### **1. Пошук транзитних екзопланет з повними характеристиками:**

```sql
SELECT 
    pl_name, hostname, 
    pl_orbper, pl_orbpererr1, pl_orbpererr2,
    pl_trandep, pl_trandeperr1, pl_trandeperr2,
    pl_trandur, pl_trandurerr1, pl_trandurerr2,
    pl_tranmid, pl_tranmiderr1, pl_tranmiderr2,
    pl_rade, pl_radeerr1, pl_radeerr2,
    pl_masse, pl_masseerr1, pl_masseerr2,
    st_teff, st_tefferr1, st_tefferr2,
    st_rad, st_raderr1, st_raderr2,
    st_mass, st_masserr1, st_masserr2,
    sy_dist, sy_disterr1, sy_disterr2,
    ra, dec, sy_vmag, sy_kmag,
    disc_year, disc_facility, discoverymethod
FROM ps 
WHERE pl_tranflag = 1 
AND pl_orbper IS NOT NULL 
AND pl_trandep IS NOT NULL
AND st_teff IS NOT NULL
ORDER BY pl_trandep DESC
```

### **2. Пошук планет придатних для атмосферних досліджень:**

```sql
SELECT 
    pl_name, hostname,
    pl_orbper, pl_trandep, pl_rade,
    st_teff, st_rad, sy_kmag,
    (pl_rade * pl_trandep * 1000000) / (sy_kmag * sy_kmag) AS transmission_metric
FROM ps 
WHERE pl_tranflag = 1 
AND pl_rade BETWEEN 1 AND 4
AND st_teff BETWEEN 4000 AND 7000
AND sy_kmag < 12
ORDER BY transmission_metric DESC
```

### **3. Статистика за методами відкриття:**

```sql
SELECT 
    discoverymethod,
    COUNT(*) as count,
    AVG(pl_rade) as avg_radius,
    AVG(pl_orbper) as avg_period,
    AVG(pl_trandep) as avg_depth
FROM ps 
WHERE pl_tranflag = 1
GROUP BY discoverymethod
ORDER BY count DESC
```

---

## 📊 **ЯКІСТЬ ТА ТОЧНІСТЬ ДАНИХ**

### **Типові Похибки NASA Даних:**

| Параметр | Типова Точність | Джерело |
|----------|-----------------|---------|
| **Орбітальний період** | 10⁻⁶ - 10⁻⁴ днів | Транзитна фотометрія |
| **Радіус планети** | 5-15% | Транзитна глибина + зоряний радіус |
| **Маса планети** | 10-30% | Радіальні швидкості |
| **Зоряна температура** | 50-150 K | Спектроскопія |
| **Зоряний радіус** | 5-20% | Астеросейсмологія/ізохрони |
| **Відстань** | 1-10% | Gaia паралакси |

### **Прапорці Якості TESS:**

```python
TESS_QUALITY_FLAGS = {
    1: "Attitude tweak",
    2: "Safe mode",
    4: "Coarse point",
    8: "Earth point",
    16: "Argabrightening",
    32: "Reaction wheel desaturation",
    64: "Manual exclude",
    128: "Discontinuity",
    256: "Impulsive outlier",
    512: "Argabrightening",
    1024: "Cosmic ray",
    2048: "Straylight",
    4096: "Straylight",
    8192: "Straylight"
}
```

---

## 🔧 **ПРАКТИЧНЕ ВИКОРИСТАННЯ**

### **Завантаження даних через Python:**

```python
from nasa_data_loader import NASAExoplanetDataLoader

# Ініціалізація
loader = NASAExoplanetDataLoader()

# Отримати список планет
planets = loader.get_confirmed_planets_list(limit=100)

# Завантажити характеристики конкретної планети
characteristics = loader.get_target_characteristics('HD 209458 b')

# Завантажити lightcurve дані
lightcurve, metadata = loader.download_tess_lightcurve('HD 209458 b')

# Повний аналіз
from nasa_analysis_system import NASAExoplanetAnalysisSystem
analyzer = NASAExoplanetAnalysisSystem()
results = analyzer.analyze_nasa_target('HD 209458 b')
```

### **Доступні Цілі для Аналізу:**

1. **HD 209458 b** - Перша транзитна екзопланета
2. **WASP-12b** - Гарячий Юпітер з коротким періодом
3. **Kepler-7b** - Планета з відомою атмосферою
4. **TRAPPIST-1 e** - Планета в зоні життя
5. **TOI-715 b** - Недавно відкрита планета TESS
6. **K2-18 b** - Суб-Нептун з водяною парою
7. **55 Cnc e** - Надземля з лавовою поверхнею

---

## 🎯 **ВИСНОВКИ**

NASA надає **найповнішу базу даних** екзопланет з усіма необхідними характеристиками:

✅ **Зоряні параметри** - температура, радіус, маса, металічність  
✅ **Планетарні властивості** - розмір, маса, орбіта, температура  
✅ **Транзитні дані** - глибина, тривалість, епоха, геометрія  
✅ **Спостережні метадані** - координати, відстань, відкриття  
✅ **Lightcurve дані** - високоякісні часові ряди з TESS/Kepler  
✅ **Похибки та якість** - повна інформація про точність  

Ця система дозволяє проводити **професійний аналіз** на рівні наукових публікацій!