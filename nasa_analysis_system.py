#!/usr/bin/env python3
"""
Повна система аналізу NASA даних з професійним детектором екзопланет
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from nasa_data_loader import NASAExoplanetDataLoader
from professional_detection import ProfessionalExoplanetDetector
import seaborn as sns

class NASAExoplanetAnalysisSystem:
    """
    Повна система для аналізу справжніх NASA даних
    """
    
    def __init__(self):
        self.data_loader = NASAExoplanetDataLoader()
        self.detector = ProfessionalExoplanetDetector()
        
    def analyze_nasa_target(self, target_name, mission='TESS'):
        """
        Повний аналіз NASA цілі з усіма характеристиками
        """
        print(f"🌟 ПОВНИЙ АНАЛІЗ NASA ДАНИХ")
        print(f"Ціль: {target_name}")
        print(f"Місія: {mission}")
        print("=" * 60)
        
        # 1. Завантажити характеристики цілі
        print("1️⃣ Завантажуємо характеристики з NASA Exoplanet Archive...")
        characteristics = self.data_loader.get_target_characteristics(target_name)
        
        # 2. Завантажити lightcurve дані
        print("2️⃣ Завантажуємо lightcurve дані...")
        if mission.upper() == 'TESS':
            lightcurve_data, metadata = self.data_loader.download_tess_lightcurve(target_name)
        elif mission.upper() == 'KEPLER':
            lightcurve_data, metadata = self.data_loader.download_kepler_lightcurve(target_name)
        else:
            raise ValueError(f"Непідтримувана місія: {mission}")
        
        # 3. Підготувати дані для аналізу
        print("3️⃣ Підготовка даних для професійного аналізу...")
        analysis_data = self._prepare_analysis_data(lightcurve_data, metadata)
        
        # 4. Запустити професійний детектор
        print("4️⃣ Запуск професійного детектора екзопланет...")
        detection_results = self.detector.analyze_lightcurve(analysis_data)
        
        # 5. Порівняти з відомими параметрами
        print("5️⃣ Порівняння з каталогізованими параметрами...")
        comparison = self._compare_with_catalog(detection_results, characteristics, metadata)
        
        # 6. Створити повний звіт
        print("6️⃣ Створення повного звіту...")
        full_report = self._generate_full_report(
            target_name, lightcurve_data, metadata, characteristics, 
            detection_results, comparison
        )
        
        # 7. Створити професійні графіки
        print("7️⃣ Створення професійних візуалізацій...")
        self._create_professional_plots(
            target_name, lightcurve_data, metadata, detection_results, comparison
        )
        
        return full_report
    
    def _prepare_analysis_data(self, lightcurve_data, metadata):
        """
        Підготувати дані у форматі для професійного детектора
        """
        # Конвертувати у стандартний формат
        analysis_data = pd.DataFrame({
            'time': lightcurve_data['time'].values,
            'flux': lightcurve_data['flux'].values,
            'flux_err': lightcurve_data['flux_err'].values
        })
        
        # Видалити NaN значення
        analysis_data = analysis_data.dropna()
        
        # Нормалізувати потік
        median_flux = np.median(analysis_data['flux'])
        analysis_data['flux'] = analysis_data['flux'] / median_flux
        analysis_data['flux_err'] = analysis_data['flux_err'] / median_flux
        
        return analysis_data
    
    def _compare_with_catalog(self, detection_results, characteristics, metadata):
        """
        Порівняти результати детекції з каталогізованими параметрами
        """
        comparison = {
            'catalog_params': {},
            'detected_params': {},
            'accuracy': {},
            'validation': {}
        }
        
        # Витягти каталогізовані параметри
        transit_props = characteristics.get('transit_properties', {})
        planetary_props = characteristics.get('planetary_properties', {})
        
        comparison['catalog_params'] = {
            'period': planetary_props.get('orbital_period'),
            'depth': transit_props.get('transit_depth'),  # у %
            'duration': transit_props.get('transit_duration'),  # у годинах
            'epoch': transit_props.get('transit_epoch')
        }
        
        # Витягти детектовані параметри
        detection = detection_results['detection']
        comparison['detected_params'] = {
            'period': detection.get('period'),
            'depth': detection.get('depth') * 100 if detection.get('depth') else None,  # конвертувати у %
            'duration': None,  # TODO: додати детекцію тривалості
            'epoch': detection.get('epoch')
        }
        
        # Розрахувати точність
        for param in ['period', 'depth']:
            catalog_val = comparison['catalog_params'].get(param)
            detected_val = comparison['detected_params'].get(param)
            
            if catalog_val and detected_val:
                error = abs(detected_val - catalog_val)
                relative_error = error / catalog_val * 100
                comparison['accuracy'][param] = {
                    'absolute_error': error,
                    'relative_error': relative_error,
                    'catalog_value': catalog_val,
                    'detected_value': detected_val
                }
        
        # Валідація детекції
        comparison['validation'] = {
            'detection_success': detection['has_transit'],
            'confidence': detection['confidence'],
            'snr': detection['snr'],
            'expected_detection': transit_props.get('transit_flag', 1) == 1
        }
        
        return comparison
    
    def _generate_full_report(self, target_name, lightcurve_data, metadata, 
                            characteristics, detection_results, comparison):
        """
        Створити повний звіт аналізу
        """
        report = {
            'target_info': {
                'name': target_name,
                'mission': metadata.get('mission'),
                'coordinates': {
                    'ra': characteristics['observational_properties'].get('right_ascension'),
                    'dec': characteristics['observational_properties'].get('declination')
                }
            },
            'data_quality': {
                'n_points': len(lightcurve_data),
                'time_span': lightcurve_data['time'].max() - lightcurve_data['time'].min(),
                'cadence': np.median(np.diff(lightcurve_data['time'])) * 24 * 60,  # хвилини
                'rms_noise': lightcurve_data['flux'].std() * 1e6  # ppm
            },
            'stellar_properties': characteristics['stellar_properties'],
            'detection_results': detection_results,
            'parameter_comparison': comparison,
            'professional_assessment': self._generate_professional_assessment(
                detection_results, comparison
            )
        }
        
        return report
    
    def _generate_professional_assessment(self, detection_results, comparison):
        """
        Створити професійну оцінку результатів
        """
        detection = detection_results['detection']
        validation = comparison['validation']
        
        assessment = {
            'detection_quality': 'Unknown',
            'parameter_accuracy': 'Unknown',
            'recommendation': 'Unknown',
            'confidence_level': detection['confidence'],
            'false_positive_probability': 1 - detection['confidence']
        }
        
        # Оцінити якість детекції
        if detection['has_transit'] and detection['confidence'] > 0.9:
            assessment['detection_quality'] = 'Excellent'
        elif detection['has_transit'] and detection['confidence'] > 0.7:
            assessment['detection_quality'] = 'Good'
        elif detection['has_transit'] and detection['confidence'] > 0.5:
            assessment['detection_quality'] = 'Fair'
        else:
            assessment['detection_quality'] = 'Poor'
        
        # Оцінити точність параметрів
        period_accuracy = comparison['accuracy'].get('period', {})
        if period_accuracy and period_accuracy['relative_error'] < 1:
            assessment['parameter_accuracy'] = 'Excellent'
        elif period_accuracy and period_accuracy['relative_error'] < 5:
            assessment['parameter_accuracy'] = 'Good'
        elif period_accuracy and period_accuracy['relative_error'] < 10:
            assessment['parameter_accuracy'] = 'Fair'
        else:
            assessment['parameter_accuracy'] = 'Poor'
        
        # Рекомендації
        if assessment['detection_quality'] == 'Excellent':
            assessment['recommendation'] = 'Confirmed exoplanet candidate. Recommend for follow-up observations.'
        elif assessment['detection_quality'] == 'Good':
            assessment['recommendation'] = 'Strong candidate. Additional validation recommended.'
        elif assessment['detection_quality'] == 'Fair':
            assessment['recommendation'] = 'Marginal detection. Requires improved data or analysis.'
        else:
            assessment['recommendation'] = 'No convincing detection. Consider alternative methods.'
        
        return assessment
    
    def _create_professional_plots(self, target_name, lightcurve_data, metadata, 
                                 detection_results, comparison):
        """
        Створити професійні графіки для публікації
        """
        # Налаштування стилю для публікації
        plt.style.use('seaborn-v0_8-whitegrid')
        fig = plt.figure(figsize=(16, 12))
        
        # Створити сітку графіків
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        time = lightcurve_data['time'].values
        flux = lightcurve_data['flux'].values
        
        # 1. Повна lightcurve
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(time, flux, 'k.', markersize=0.3, alpha=0.6)
        ax1.set_title(f'{target_name} - Full Light Curve ({metadata["mission"]})', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Relative Flux')
        ax1.grid(True, alpha=0.3)
        
        # Позначити транзити якщо детектовано
        detection = detection_results['detection']
        if detection['has_transit'] and detection.get('period'):
            period = detection['period']
            epoch = detection.get('epoch', time[0])
            
            # Розрахувати часи транзитів
            transit_times = []
            t = epoch
            while t < time.max():
                if t >= time.min():
                    transit_times.append(t)
                t += period
            
            for tt in transit_times:
                ax1.axvline(tt, color='red', alpha=0.7, linestyle='--', linewidth=1)
        
        # 2. Збільшений вигляд транзиту
        ax2 = fig.add_subplot(gs[1, 0])
        if detection['has_transit'] and len(transit_times) > 0:
            # Показати перший транзит
            first_transit = transit_times[0]
            window = 0.5  # days
            mask = np.abs(time - first_transit) < window
            
            if np.any(mask):
                ax2.plot(time[mask], flux[mask], 'b.', markersize=1, alpha=0.8)
                ax2.axvline(first_transit, color='red', alpha=0.7, linestyle='--')
                ax2.set_title('Transit Zoom-in')
                ax2.set_ylabel('Relative Flux')
                ax2.grid(True, alpha=0.3)
        
        # 3. Фазово-згорнутий транзит
        ax3 = fig.add_subplot(gs[1, 1])
        if detection['has_transit'] and detection.get('period'):
            period = detection['period']
            epoch = detection.get('epoch', time[0])
            
            # Фазове згортання
            phase = ((time - epoch) % period) / period
            phase[phase > 0.5] -= 1  # Центрувати на транзиті
            
            # Сортувати за фазою
            sort_idx = np.argsort(phase)
            phase_sorted = phase[sort_idx]
            flux_sorted = flux[sort_idx]
            
            ax3.plot(phase_sorted * 24, flux_sorted, 'r.', markersize=0.8, alpha=0.6)
            ax3.set_title(f'Phase-folded Transit\n(P = {period:.4f} d)')
            ax3.set_xlabel('Hours from mid-transit')
            ax3.set_ylabel('Relative Flux')
            ax3.grid(True, alpha=0.3)
        
        # 4. Порівняння параметрів
        ax4 = fig.add_subplot(gs[1, 2])
        comparison_data = []
        labels = []
        
        for param in ['period', 'depth']:
            accuracy = comparison['accuracy'].get(param)
            if accuracy:
                comparison_data.append([
                    accuracy['catalog_value'],
                    accuracy['detected_value']
                ])
                labels.append(f"{param.title()}\n({accuracy['relative_error']:.1f}% error)")
        
        if comparison_data:
            comparison_array = np.array(comparison_data)
            x_pos = np.arange(len(labels))
            
            width = 0.35
            ax4.bar(x_pos - width/2, comparison_array[:, 0], width, 
                   label='Catalog', alpha=0.8, color='blue')
            ax4.bar(x_pos + width/2, comparison_array[:, 1], width,
                   label='Detected', alpha=0.8, color='red')
            
            ax4.set_title('Parameter Comparison')
            ax4.set_xticks(x_pos)
            ax4.set_xticklabels(labels)
            ax4.legend()
            ax4.grid(True, alpha=0.3)
        
        # 5. Статистики детекції
        ax5 = fig.add_subplot(gs[2, 0])
        
        metrics = ['SNR', 'Confidence', 'Validation']
        values = [
            detection.get('snr', 0),
            detection['confidence'] * 100,
            detection.get('validation_score', 0) * 100
        ]
        colors = ['green' if v > 70 else 'orange' if v > 40 else 'red' for v in values]
        
        bars = ax5.bar(metrics, values, color=colors, alpha=0.7)
        ax5.set_title('Detection Metrics')
        ax5.set_ylabel('Score')
        ax5.grid(True, alpha=0.3)
        
        # Додати значення на стовпчики
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{value:.1f}', ha='center', va='bottom')
        
        # 6. Розподіл шуму
        ax6 = fig.add_subplot(gs[2, 1])
        
        # Розрахувати залишки
        if detection['has_transit']:
            # Простий тренд для демонстрації
            trend = np.polyval(np.polyfit(time, flux, 2), time)
            residuals = flux - trend
        else:
            residuals = flux - np.median(flux)
        
        ax6.hist(residuals * 1e6, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        ax6.set_title(f'Noise Distribution\n(RMS = {np.std(residuals)*1e6:.0f} ppm)')
        ax6.set_xlabel('Residuals (ppm)')
        ax6.set_ylabel('Frequency')
        ax6.grid(True, alpha=0.3)
        
        # 7. Професійний звіт
        ax7 = fig.add_subplot(gs[2, 2])
        ax7.axis('off')
        
        # Текстовий звіт
        report_text = f"""DETECTION SUMMARY
        
Target: {target_name}
Mission: {metadata['mission']}

RESULTS:
• Transit: {'DETECTED' if detection['has_transit'] else 'NOT DETECTED'}
• Confidence: {detection['confidence']*100:.1f}%
• SNR: {detection.get('snr', 0):.1f}σ

PARAMETERS:
"""
        
        if detection.get('period'):
            report_text += f"• Period: {detection['period']:.4f} d\n"
        if detection.get('depth'):
            report_text += f"• Depth: {detection['depth']*100:.3f}%\n"
        
        # Додати порівняння з каталогом
        period_acc = comparison['accuracy'].get('period')
        if period_acc:
            report_text += f"\nACCURACY:\n• Period: {period_acc['relative_error']:.1f}% error"
        
        ax7.text(0.05, 0.95, report_text, transform=ax7.transAxes, 
                fontsize=10, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        plt.suptitle(f'Professional Exoplanet Analysis: {target_name}', 
                    fontsize=16, fontweight='bold')
        
        # Зберегти графік
        filename = f'/workspace/nasa_analysis_{target_name.replace(" ", "_")}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"📊 Професійні графіки збережено: {filename}")
    
    def batch_analyze_targets(self, target_list):
        """
        Пакетний аналіз кількох цілей
        """
        print(f"🚀 ПАКЕТНИЙ АНАЛІЗ {len(target_list)} ЦІЛЕЙ")
        print("=" * 60)
        
        results = {}
        
        for i, target in enumerate(target_list, 1):
            print(f"\n📍 Аналіз {i}/{len(target_list)}: {target}")
            print("-" * 40)
            
            try:
                result = self.analyze_nasa_target(target)
                results[target] = result
                
                # Короткий звіт
                detection = result['detection_results']['detection']
                print(f"✅ {target}: {'DETECTED' if detection['has_transit'] else 'NOT DETECTED'} "
                      f"(Confidence: {detection['confidence']*100:.1f}%)")
                
            except Exception as e:
                print(f"❌ Помилка аналізу {target}: {e}")
                results[target] = {'error': str(e)}
        
        # Створити зведений звіт
        self._create_batch_summary(results)
        
        return results
    
    def _create_batch_summary(self, results):
        """
        Створити зведений звіт пакетного аналізу
        """
        print(f"\n📊 ЗВЕДЕНИЙ ЗВІТ ПАКЕТНОГО АНАЛІЗУ")
        print("=" * 60)
        
        successful_analyses = {k: v for k, v in results.items() if 'error' not in v}
        
        print(f"Успішно проаналізовано: {len(successful_analyses)}/{len(results)} цілей")
        
        if successful_analyses:
            # Статистика детекції
            detections = [v['detection_results']['detection']['has_transit'] 
                         for v in successful_analyses.values()]
            detection_rate = sum(detections) / len(detections) * 100
            
            print(f"Рівень детекції: {detection_rate:.1f}%")
            
            # Таблиця результатів
            print(f"\n{'Target':<20} {'Detected':<10} {'Confidence':<12} {'Period':<10} {'Accuracy'}")
            print("-" * 70)
            
            for target, result in successful_analyses.items():
                detection = result['detection_results']['detection']
                comparison = result['parameter_comparison']
                
                detected = "YES" if detection['has_transit'] else "NO"
                confidence = f"{detection['confidence']*100:.1f}%"
                period = f"{detection.get('period', 0):.3f}" if detection.get('period') else "N/A"
                
                period_acc = comparison['accuracy'].get('period')
                accuracy = f"{period_acc['relative_error']:.1f}%" if period_acc else "N/A"
                
                print(f"{target:<20} {detected:<10} {confidence:<12} {period:<10} {accuracy}")

def main():
    """Демонстрація повної системи аналізу NASA даних"""
    
    print("🌟 NASA EXOPLANET ANALYSIS SYSTEM")
    print("Повна система аналізу справжніх NASA даних")
    print("=" * 60)
    
    # Ініціалізувати систему
    analysis_system = NASAExoplanetAnalysisSystem()
    
    # Список цілей для аналізу
    targets = [
        'HD 209458 b',
        'WASP-12b', 
        'Kepler-7b',
        'TRAPPIST-1 e'
    ]
    
    print(f"\n🎯 Цілі для аналізу: {', '.join(targets)}")
    
    # Проаналізувати одну ціль детально
    target = targets[0]
    print(f"\n🔍 Детальний аналіз: {target}")
    result = analysis_system.analyze_nasa_target(target)
    
    # Показати результати
    detection = result['detection_results']['detection']
    assessment = result['professional_assessment']
    
    print(f"\n🎯 РЕЗУЛЬТАТИ ДЛЯ {target}:")
    print(f"  Детекція: {'ТАК' if detection['has_transit'] else 'НІ'}")
    print(f"  Впевненість: {detection['confidence']*100:.1f}%")
    print(f"  Якість детекції: {assessment['detection_quality']}")
    print(f"  Точність параметрів: {assessment['parameter_accuracy']}")
    print(f"  Рекомендація: {assessment['recommendation']}")
    
    # Пакетний аналіз (опціонально)
    print(f"\n🚀 Запустити пакетний аналіз всіх цілей? (y/n)")
    # batch_results = analysis_system.batch_analyze_targets(targets)
    
    print(f"\n✅ Аналіз завершено!")
    print(f"📊 Перевірте створені графіки та звіти")

if __name__ == "__main__":
    main()