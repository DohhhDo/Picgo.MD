using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Controls.Primitives;
using System;
using System.Threading.Tasks;
using Windows.Storage.Pickers;
using Windows.Storage;

namespace MdImgConverter
{
    public sealed partial class MainWindow : Window
    {
        public MainWindow()
        {
            this.InitializeComponent();
            this.Title = "MdImgConverter - Win11原生应用";
        }

        private void QualitySlider_ValueChanged(object sender, RangeBaseValueChangedEventArgs e)
        {
            if (QualityLabel != null)
            {
                QualityLabel.Text = $"{(int)e.NewValue}%";
            }
        }

        private void PresetButton_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button button && button.Tag is string qualityStr)
            {
                if (int.TryParse(qualityStr, out int quality))
                {
                    QualitySlider.Value = quality;
                    
                    // 更新按钮样式，显示选中状态
                    ResetPresetButtons();
                    button.Style = (Style)Application.Current.Resources["AccentButtonStyle"];
                }
            }
        }

        private void ResetPresetButtons()
        {
            // 重置所有预设按钮样式
            var defaultStyle = (Style)Application.Current.Resources["DefaultButtonStyle"];
            // 这里需要遍历所有预设按钮并重置样式
        }

        private async void ConvertButton_Click(object sender, RoutedEventArgs e)
        {
            ConvertButton.IsEnabled = false;
            ProgressText.Text = "开始转换...";
            
            // 模拟转换过程
            for (int i = 0; i <= 100; i += 5)
            {
                ConversionProgress.Value = i;
                ProgressText.Text = i == 100 ? "转换完成!" : $"转换中... {i}%";
                await Task.Delay(100);
            }
            
            // 重置状态
            await Task.Delay(2000);
            ConversionProgress.Value = 0;
            ProgressText.Text = "准备就绪";
            ConvertButton.IsEnabled = true;
        }
    }
}
