using Microsoft.UI.Xaml;
using System;

namespace MdImgConverter
{
    public static class Program
    {
        [STAThread]
        public static void Main(string[] args)
        {
            Microsoft.UI.Xaml.Application.Start((p) =>
            {
                var app = new App();
                return app;
            });
        }
    }
}

