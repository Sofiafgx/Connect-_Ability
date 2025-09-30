#!/usr/bin/env python3
"""
Простий приклад NASA даних без зовнішніх залежностей
"""

def show_nasa_data_characteristics():
    """Показати всі характеристики NASA даних"""
    
    print("🌟 NASA EXOPLANET DATA - ВСІ ДОСТУПНІ ХАРАКТЕРИСТИКИ")
    print("=" * 70)
    
    # Приклад реальних даних з NASA Exoplanet Archive
    example_planets = {
        'HD 209458 b': {
            'stellar_properties': {
                'effective_temperature': 6065,  # K
                'stellar_radius': 1.155,        # R☉
                'stellar_mass': 1.119,          # M☉
                'metallicity': 0.00,            # [Fe/H]
                'surface_gravity': 4.361,       # log g
                'magnitude_v': 7.65,            # mag
                'magnitude_k': 6.308            # mag
            },
            'planetary_properties': {
                'planet_radius': 1.359,         # R_Jup
                'planet_mass': 0.685,           # M_Jup
                'orbital_period': 3.52474859,   # days
                'semi_major_axis': 0.04747,     # AU
                'eccentricity': 0.067,          # 
                'inclination': 86.71,           # degrees
                'equilibrium_temperature': 1449 # K
            },
            'transit_properties': {
                'transit_depth': 1.56,          # %
                'transit_duration': 3.061,      # hours
                'transit_epoch': 2452826.628521, # BJD
                'impact_parameter': 0.507,      # b
                'a_over_rs': 8.76,             # a/Rs
                'rp_over_rs': 0.12094          # Rp/Rs
            },
            'observational_properties': {
                'right_ascension': 330.7949,   # degrees
                'declination': 18.8842,        # degrees
                'distance': 47.0,              # parsecs
                'discovery_year': 1999,
                'discovery_method': 'Transit',
                'discovery_facility': 'Multiple'
            }
        },
        
        'WASP-12b': {
            'stellar_properties': {
                'effective_temperature': 6300,
                'stellar_radius': 1.599,
                'stellar_mass': 1.434,
                'metallicity': 0.30,
                'surface_gravity': 4.17,
                'magnitude_v': 11.69,
                'magnitude_k': 10.47
            },
            'planetary_properties': {
                'planet_radius': 1.79,
                'planet_mass': 1.47,
                'orbital_period': 1.09142245,
                'semi_major_axis': 0.0229,
                'eccentricity': 0.049,
                'inclination': 83.1,
                'equilibrium_temperature': 2516
            },
            'transit_properties': {
                'transit_depth': 1.41,
                'transit_duration': 2.18,
                'transit_epoch': 2454508.9761,
                'impact_parameter': 0.363,
                'a_over_rs': 3.09,
                'rp_over_rs': 0.1187
            },
            'observational_properties': {
                'right_ascension': 97.6367,
                'declination': 29.6722,
                'distance': 427.0,
                'discovery_year': 2008,
                'discovery_method': 'Transit',
                'discovery_facility': 'SuperWASP'
            }
        },
        
        'Kepler-7b': {
            'stellar_properties': {
                'effective_temperature': 5933,
                'stellar_radius': 1.843,
                'stellar_mass': 1.347,
                'metallicity': 0.11,
                'surface_gravity': 4.08,
                'magnitude_v': 13.0,
                'magnitude_k': 11.5
            },
            'planetary_properties': {
                'planet_radius': 1.478,
                'planet_mass': 0.433,
                'orbital_period': 4.8854892,
                'semi_major_axis': 0.06224,
                'eccentricity': 0.0,
                'inclination': 86.8,
                'equilibrium_temperature': 1540
            },
            'transit_properties': {
                'transit_depth': 0.065,
                'transit_duration': 4.17,
                'transit_epoch': 2454966.5281,
                'impact_parameter': 0.108,
                'a_over_rs': 4.93,
                'rp_over_rs': 0.08016
            },
            'observational_properties': {
                'right_ascension': 287.1789,
                'declination': 41.9133,
                'distance': 1044.0,
                'discovery_year': 2010,
                'discovery_method': 'Transit',
                'discovery_facility': 'Kepler'
            }
        }
    }
    
    print("\n📋 ПРИКЛАДИ РЕАЛЬНИХ NASA ДАНИХ:")
    print("=" * 50)
    
    for planet_name, data in example_planets.items():
        print(f"\n🪐 {planet_name}")
        print("-" * 30)
        
        # Зоряні властивості
        stellar = data['stellar_properties']
        print(f"🌟 ЗОРЯНІ ВЛАСТИВОСТІ:")
        print(f"  Температура: {stellar['effective_temperature']} K")
        print(f"  Радіус: {stellar['stellar_radius']} R☉")
        print(f"  Маса: {stellar['stellar_mass']} M☉")
        print(f"  Металічність: {stellar['metallicity']:+.2f} dex")
        print(f"  Зоряна величина V: {stellar['magnitude_v']} mag")
        
        # Планетарні властивості
        planetary = data['planetary_properties']
        print(f"\n🪐 ПЛАНЕТАРНІ ВЛАСТИВОСТІ:")
        print(f"  Радіус: {planetary['planet_radius']} R_Jup")
        print(f"  Маса: {planetary['planet_mass']} M_Jup")
        print(f"  Період: {planetary['orbital_period']:.6f} днів")
        print(f"  Велика піввісь: {planetary['semi_major_axis']} AU")
        print(f"  Температура: {planetary['equilibrium_temperature']} K")
        
        # Транзитні властивості
        transit = data['transit_properties']
        print(f"\n🌅 ТРАНЗИТНІ ВЛАСТИВОСТІ:")
        print(f"  Глибина: {transit['transit_depth']:.3f}%")
        print(f"  Тривалість: {transit['transit_duration']:.2f} годин")
        print(f"  Епоха: {transit['transit_epoch']:.6f} BJD")
        print(f"  Параметр удару: {transit['impact_parameter']:.3f}")
        
        # Спостережні властивості
        observational = data['observational_properties']
        print(f"\n🔭 СПОСТЕРЕЖНІ ВЛАСТИВОСТІ:")
        print(f"  Координати: RA {observational['right_ascension']:.4f}°, Dec {observational['declination']:.4f}°")
        print(f"  Відстань: {observational['distance']} пк")
        print(f"  Відкриття: {observational['discovery_year']} ({observational['discovery_facility']})")

def show_lightcurve_data_structure():
    """Показати структуру lightcurve даних"""
    
    print(f"\n🛰️ СТРУКТУРА LIGHTCURVE ДАНИХ")
    print("=" * 40)
    
    # TESS структура даних
    print(f"\n📡 TESS LIGHTCURVE ДАНІ:")
    tess_columns = {
        'TIME': 'BJD - 2457000 (Barycentric Julian Date)',
        'FLUX': 'e-/s (електрони за секунду)',
        'FLUX_ERR': 'e-/s (похибка потоку)',
        'QUALITY': 'bitmask (прапорці якості)',
        'CADENCENO': 'int (номер кадру)',
        'SAP_FLUX': 'e-/s (Simple Aperture Photometry)',
        'PDCSAP_FLUX': 'e-/s (Pre-search Data Conditioning)',
        'CENTROID_COL': 'pixels (центроїд по стовпцях)',
        'CENTROID_ROW': 'pixels (центроїд по рядках)'
    }
    
    for col, desc in tess_columns.items():
        print(f"  {col:<15}: {desc}")
    
    # Kepler структура даних
    print(f"\n🔭 KEPLER LIGHTCURVE ДАНІ:")
    kepler_columns = {
        'TIME': 'BJD - 2454833 (Kepler BJD epoch)',
        'FLUX': 'e-/s (калібрований потік)',
        'FLUX_ERR': 'e-/s (похибка потоку)',
        'QUALITY': 'bitmask (прапорці якості)',
        'SAP_FLUX': 'e-/s (SAP потік)',
        'PDCSAP_FLUX': 'e-/s (PDC потік)',
        'SAP_BKG': 'e-/s (фон SAP)',
        'POS_CORR1': 'pixels (корекція позиції 1)',
        'POS_CORR2': 'pixels (корекція позиції 2)'
    }
    
    for col, desc in kepler_columns.items():
        print(f"  {col:<15}: {desc}")

def show_data_quality_info():
    """Показати інформацію про якість даних"""
    
    print(f"\n📊 ЯКІСТЬ ТА ТОЧНІСТЬ NASA ДАНИХ")
    print("=" * 40)
    
    quality_info = {
        'Орбітальний період': {
            'точність': '10⁻⁶ - 10⁻⁴ днів',
            'джерело': 'Транзитна фотометрія',
            'приклад': 'HD 209458 b: 3.52474859 ± 0.00000038 днів'
        },
        'Радіус планети': {
            'точність': '5-15%',
            'джерело': 'Глибина транзиту + зоряний радіус',
            'приклад': 'HD 209458 b: 1.359 ± 0.019 R_Jup'
        },
        'Маса планети': {
            'точність': '10-30%',
            'джерело': 'Радіальні швидкості',
            'приклад': 'HD 209458 b: 0.685 ± 0.015 M_Jup'
        },
        'Зоряна температура': {
            'точність': '50-150 K',
            'джерело': 'Спектроскопія',
            'приклад': 'HD 209458: 6065 ± 50 K'
        },
        'Глибина транзиту': {
            'точність': '0.001-0.01%',
            'джерело': 'Високоточна фотометрія',
            'приклад': 'HD 209458 b: 1.56 ± 0.02%'
        }
    }
    
    for param, info in quality_info.items():
        print(f"\n📈 {param}:")
        print(f"  Точність: {info['точність']}")
        print(f"  Джерело: {info['джерело']}")
        print(f"  Приклад: {info['приклад']}")

def show_analysis_capabilities():
    """Показати можливості аналізу"""
    
    print(f"\n🔬 МОЖЛИВОСТІ ПРОФЕСІЙНОГО АНАЛІЗУ")
    print("=" * 45)
    
    capabilities = [
        "✅ Автоматичне завантаження даних з NASA Exoplanet Archive",
        "✅ Повні характеристики зірок (температура, радіус, маса, металічність)",
        "✅ Детальні параметри планет (розмір, маса, орбіта, температура)",
        "✅ Транзитні властивості (глибина, тривалість, епоха, геометрія)",
        "✅ Lightcurve дані з TESS та Kepler з повними метаданими",
        "✅ Професійне видалення артефактів (PCA, регресія, фільтрація)",
        "✅ Box Least Squares (BLS) пошук транзитів",
        "✅ Валідація детекції (форма транзиту, періодичність, вторинне затемнення)",
        "✅ Порівняння з каталогізованими параметрами",
        "✅ Оцінка точності та надійності детекції",
        "✅ Професійні графіки та звіти для публікацій",
        "✅ Пакетний аналіз множинних цілей"
    ]
    
    for capability in capabilities:
        print(f"  {capability}")

def show_usage_examples():
    """Показати приклади використання"""
    
    print(f"\n🚀 ПРИКЛАДИ ВИКОРИСТАННЯ")
    print("=" * 30)
    
    print(f"""
# 1. Завантаження списку екзопланет
loader = NASAExoplanetDataLoader()
planets = loader.get_confirmed_planets_list(limit=100)

# 2. Отримання характеристик конкретної планети
characteristics = loader.get_target_characteristics('HD 209458 b')

# 3. Завантаження lightcurve даних
lightcurve, metadata = loader.download_tess_lightcurve('HD 209458 b')

# 4. Повний професійний аналіз
analyzer = NASAExoplanetAnalysisSystem()
results = analyzer.analyze_nasa_target('HD 209458 b')

# 5. Пакетний аналіз кількох цілей
targets = ['HD 209458 b', 'WASP-12b', 'Kepler-7b']
batch_results = analyzer.batch_analyze_targets(targets)
""")

def main():
    """Головна функція демонстрації"""
    
    print("🌟 ДЕМОНСТРАЦІЯ NASA EXOPLANET DATA")
    print("Всі характеристики доступні для професійного аналізу")
    print("=" * 70)
    
    # Показати всі можливості
    show_nasa_data_characteristics()
    show_lightcurve_data_structure()
    show_data_quality_info()
    show_analysis_capabilities()
    show_usage_examples()
    
    print(f"\n🎯 ДОСТУПНІ ФАЙЛИ ДЛЯ РОБОТИ:")
    print(f"  📊 nasa_data_loader.py - Завантажувач NASA даних")
    print(f"  🔬 professional_detection.py - Професійний детектор")
    print(f"  🚀 nasa_analysis_system.py - Повна система аналізу")
    print(f"  📖 NASA_DATA_CHARACTERISTICS.md - Детальна документація")
    print(f"  📋 PROFESSIONAL_METHODS.md - Методологія аналізу")
    
    print(f"\n✨ ЗАПУСК АНАЛІЗУ:")
    print(f"  python3 nasa_analysis_system.py  # Повний аналіз")
    print(f"  python3 professional_detection.py  # Тест детектора")
    print(f"  python3 test_professional.py  # Тест системи")
    
    print(f"\n🌟 Система готова для аналізу справжніх NASA даних!")

if __name__ == "__main__":
    main()