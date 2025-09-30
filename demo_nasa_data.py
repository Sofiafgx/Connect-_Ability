#!/usr/bin/env python3
"""
Демонстрація роботи з реальними NASA даними
"""

from nasa_data_loader import NASAExoplanetDataLoader
from nasa_analysis_system import NASAExoplanetAnalysisSystem

def demo_nasa_data_access():
    """Демонстрація доступу до NASA даних"""
    
    print("🌟 ДЕМОНСТРАЦІЯ NASA ДАНИХ З УСІМА ХАРАКТЕРИСТИКАМИ")
    print("=" * 70)
    
    # Ініціалізувати завантажувач
    loader = NASAExoplanetDataLoader()
    
    print("\n1️⃣ СПИСОК ПІДТВЕРДЖЕНИХ ЕКЗОПЛАНЕТ")
    print("-" * 40)
    
    # Завантажити список планет
    planets_df = loader.get_confirmed_planets_list(limit=10)
    
    print("📋 Топ-10 екзопланет з найглибшими транзитами:")
    print(f"{'Планета':<25} {'Зірка':<15} {'Період (дні)':<12} {'Глибина (%)':<12} {'Рік'}")
    print("-" * 80)
    
    for _, planet in planets_df.head(10).iterrows():
        name = planet.get('pl_name', 'N/A')[:24]
        host = planet.get('hostname', 'N/A')[:14]
        period = planet.get('pl_orbper', 0)
        depth = planet.get('pl_trandep', 0)
        year = planet.get('disc_year', 0)
        
        print(f"{name:<25} {host:<15} {period:<12.3f} {depth:<12.3f} {year}")
    
    print("\n2️⃣ ДЕТАЛЬНІ ХАРАКТЕРИСТИКИ КОНКРЕТНОЇ ПЛАНЕТИ")
    print("-" * 50)
    
    target = 'HD 209458 b'
    print(f"🎯 Аналізуємо: {target}")
    
    # Завантажити всі характеристики
    characteristics = loader.get_target_characteristics(target)
    
    print(f"\n🌟 ЗОРЯНІ ВЛАСТИВОСТІ:")
    stellar = characteristics['stellar_properties']
    print(f"  Температура: {stellar.get('effective_temperature', 'N/A')} K")
    print(f"  Радіус: {stellar.get('stellar_radius', 'N/A')} R☉")
    print(f"  Маса: {stellar.get('stellar_mass', 'N/A')} M☉")
    print(f"  Металічність: {stellar.get('metallicity', 'N/A')}")
    print(f"  Зоряна величина V: {stellar.get('magnitude_v', 'N/A')}")
    
    print(f"\n🪐 ПЛАНЕТАРНІ ВЛАСТИВОСТІ:")
    planetary = characteristics['planetary_properties']
    print(f"  Радіус планети: {planetary.get('planet_radius', 'N/A')} R⊕")
    print(f"  Маса планети: {planetary.get('planet_mass', 'N/A')} M⊕")
    print(f"  Орбітальний період: {planetary.get('orbital_period', 'N/A')} днів")
    print(f"  Велика піввісь: {planetary.get('semi_major_axis', 'N/A')} AU")
    print(f"  Ексцентриситет: {planetary.get('eccentricity', 'N/A')}")
    print(f"  Температура рівноваги: {planetary.get('equilibrium_temperature', 'N/A')} K")
    
    print(f"\n🌅 ТРАНЗИТНІ ВЛАСТИВОСТІ:")
    transit = characteristics['transit_properties']
    print(f"  Глибина транзиту: {transit.get('transit_depth', 'N/A')}%")
    print(f"  Тривалість транзиту: {transit.get('transit_duration', 'N/A')} годин")
    print(f"  Епоха транзиту: {transit.get('transit_epoch', 'N/A')} BJD")
    print(f"  Параметр удару: {transit.get('impact_parameter', 'N/A')}")
    
    print(f"\n🔭 СПОСТЕРЕЖНІ ВЛАСТИВОСТІ:")
    observational = characteristics['observational_properties']
    print(f"  Пряме сходження: {observational.get('right_ascension', 'N/A')}°")
    print(f"  Схилення: {observational.get('declination', 'N/A')}°")
    print(f"  Відстань: {observational.get('distance', 'N/A')} пк")
    print(f"  Рік відкриття: {observational.get('discovery_year', 'N/A')}")
    print(f"  Метод відкриття: {observational.get('discovery_method', 'N/A')}")
    print(f"  Обсерваторія: {observational.get('discovery_facility', 'N/A')}")
    
    print("\n3️⃣ ЗАВАНТАЖЕННЯ LIGHTCURVE ДАНИХ")
    print("-" * 40)
    
    # Завантажити lightcurve дані
    lightcurve_data, metadata = loader.download_tess_lightcurve(target)
    
    print(f"📊 ІНФОРМАЦІЯ ПРО LIGHTCURVE:")
    print(f"  Місія: {metadata['mission']}")
    print(f"  Сектор/Квартал: {metadata.get('sector', metadata.get('quarter', 'N/A'))}")
    print(f"  Точок даних: {len(lightcurve_data):,}")
    print(f"  Часовий діапазон: {lightcurve_data['time'].max() - lightcurve_data['time'].min():.1f} днів")
    print(f"  Кадр: {np.median(np.diff(lightcurve_data['time']))*24*60:.1f} хвилин")
    print(f"  RMS шум: {lightcurve_data['flux'].std()*1e6:.0f} ppm")
    
    # Інформація про планету
    if 'planet_params' in metadata:
        planet_params = metadata['planet_params']
        print(f"\n🪐 ПАРАМЕТРИ ПЛАНЕТИ В ДАНИХ:")
        print(f"  Період: {planet_params['period']:.6f} днів")
        print(f"  Глибина транзиту: {planet_params['depth']*100:.3f}%")
        print(f"  Тривалість: {planet_params['duration']*24:.2f} годин")
        
        # Розрахувати кількість транзитів
        time_span = lightcurve_data['time'].max() - lightcurve_data['time'].min()
        n_transits = int(time_span / planet_params['period'])
        print(f"  Очікувана кількість транзитів: {n_transits}")
    
    print("\n4️⃣ ЯКІСТЬ ДАНИХ ТА АРТЕФАКТИ")
    print("-" * 35)
    
    flux = lightcurve_data['flux'].values
    
    # Аналіз якості даних
    print(f"📈 СТАТИСТИКА ЯКОСТІ:")
    print(f"  Медіанний потік: {np.median(flux):.6f}")
    print(f"  Стандартне відхилення: {np.std(flux)*1e6:.1f} ppm")
    print(f"  Мін/Макс потік: {np.min(flux):.6f} / {np.max(flux):.6f}")
    
    # Детекція артефактів
    outliers = np.abs(flux - np.median(flux)) > 5 * np.std(flux)
    print(f"  Викиди (>5σ): {np.sum(outliers)} ({np.sum(outliers)/len(flux)*100:.2f}%)")
    
    # Систематичні тренди
    from scipy import stats
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        lightcurve_data['time'], flux
    )
    print(f"  Лінійний тренд: {slope*1e6:.2f} ppm/день (p={p_value:.3f})")
    
    print(f"\n✅ Дані NASA успішно завантажено та проаналізовано!")
    print(f"📊 Всі необхідні характеристики присутні для професійного аналізу")
    
    return lightcurve_data, metadata, characteristics

def demo_full_analysis():
    """Демонстрація повного аналізу"""
    
    print(f"\n" + "="*70)
    print("🚀 ПОВНИЙ ПРОФЕСІЙНИЙ АНАЛІЗ NASA ДАНИХ")
    print("="*70)
    
    # Ініціалізувати систему аналізу
    analysis_system = NASAExoplanetAnalysisSystem()
    
    # Проаналізувати відому екзопланету
    target = 'HD 209458 b'
    print(f"\n🎯 Запуск повного аналізу для: {target}")
    
    try:
        # Запустити повний аналіз
        results = analysis_system.analyze_nasa_target(target, mission='TESS')
        
        # Показати результати
        print(f"\n📊 РЕЗУЛЬТАТИ АНАЛІЗУ:")
        
        detection = results['detection_results']['detection']
        assessment = results['professional_assessment']
        comparison = results['parameter_comparison']
        
        print(f"  🎯 Детекція транзиту: {'ТАК' if detection['has_transit'] else 'НІ'}")
        print(f"  📈 Впевненість: {detection['confidence']*100:.1f}%")
        print(f"  📊 SNR: {detection.get('snr', 0):.1f}σ")
        print(f"  ⭐ Якість детекції: {assessment['detection_quality']}")
        print(f"  🎯 Точність параметрів: {assessment['parameter_accuracy']}")
        
        if detection.get('period'):
            print(f"  🔄 Детектований період: {detection['period']:.6f} днів")
            
        if detection.get('depth'):
            print(f"  📉 Детектована глибина: {detection['depth']*100:.3f}%")
        
        # Порівняння з каталогом
        if comparison['accuracy']:
            print(f"\n🔍 ПОРІВНЯННЯ З КАТАЛОГОМ:")
            for param, acc in comparison['accuracy'].items():
                print(f"  {param.title()}: {acc['relative_error']:.2f}% похибка")
                print(f"    Каталог: {acc['catalog_value']:.6f}")
                print(f"    Детектовано: {acc['detected_value']:.6f}")
        
        print(f"\n💡 РЕКОМЕНДАЦІЯ: {assessment['recommendation']}")
        
        return results
        
    except Exception as e:
        print(f"❌ Помилка аналізу: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    import numpy as np
    
    try:
        # Демонстрація доступу до даних
        lightcurve_data, metadata, characteristics = demo_nasa_data_access()
        
        # Демонстрація повного аналізу
        results = demo_full_analysis()
        
        print(f"\n🎉 ДЕМОНСТРАЦІЯ ЗАВЕРШЕНА!")
        print(f"📁 Перевірте створені файли:")
        print(f"  📊 nasa_data_example.png - Приклад NASA даних")
        print(f"  📈 nasa_analysis_*.png - Професійний аналіз")
        print(f"  📖 PROFESSIONAL_METHODS.md - Детальна методологія")
        
        print(f"\n🌟 ДОСТУПНІ ХАРАКТЕРИСТИКИ NASA ДАНИХ:")
        print(f"  ✅ Зоряні властивості (температура, радіус, маса, металічність)")
        print(f"  ✅ Планетарні властивості (радіус, маса, період, орбіта)")
        print(f"  ✅ Транзитні властивості (глибина, тривалість, епоха)")
        print(f"  ✅ Спостережні дані (координати, відстань, відкриття)")
        print(f"  ✅ Lightcurve дані (TESS/Kepler з повними метаданими)")
        print(f"  ✅ Професійний аналіз (BLS, валідація, порівняння)")
        
    except Exception as e:
        print(f"❌ Помилка демонстрації: {e}")
        import traceback
        traceback.print_exc()