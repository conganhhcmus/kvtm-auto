using System.Drawing;
using Emgu.CV;
using Emgu.CV.CvEnum;

namespace KvtmAuto.Infrastructure.Services;

/// <summary>
/// Emgu.CV template matching — mirrors Python image_controller.py:
/// color + 4 rotations + TM_CCOEFF_NORMED + early termination.
/// </summary>
public class ImageMatcher(IConfiguration config, ILogger<ImageMatcher> logger)
{
    private readonly string _assetsDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory, config["AssetsDir"] ?? "Automation/Assets"));

    private static readonly RotateFlags?[] Rotations =
        [null, RotateFlags.Rotate90Clockwise, RotateFlags.Rotate180, RotateFlags.Rotate90CounterClockwise];

    public (double x, double y)? FindOnScreen(byte[] screenshotPng, string assetRelPath, double threshold = 0.9)
    {
        try
        {
            var templatePath = ResolveAsset(assetRelPath);
            if (!File.Exists(templatePath))
            {
                logger.LogWarning("Asset not found: {Path}", templatePath);
                return null;
            }

            using var screenMat = new Mat();
            CvInvoke.Imdecode(screenshotPng, ImreadModes.ColorBgr, screenMat);

            using var templateBase = CvInvoke.Imread(templatePath, ImreadModes.ColorBgr);

            if (screenMat.IsEmpty || templateBase.IsEmpty) return null;

            double bestScore = double.MinValue;
            int bestX = 0, bestY = 0, bestW = templateBase.Width, bestH = templateBase.Height;

            foreach (var rotation in Rotations)
            {
                using var template = new Mat();
                if (rotation is null)
                    templateBase.CopyTo(template);
                else
                    CvInvoke.Rotate(templateBase, template, rotation.Value);

                if (template.Width > screenMat.Width || template.Height > screenMat.Height) continue;

                using var result = new Mat();
                CvInvoke.MatchTemplate(screenMat, template, result, TemplateMatchingType.CcoeffNormed);

                double minVal = 0, maxVal = 0;
                var minLoc = new Point();
                var maxLoc = new Point();
                CvInvoke.MinMaxLoc(result, ref minVal, ref maxVal, ref minLoc, ref maxLoc);

                // Early termination — same as Python
                if (maxVal >= threshold)
                    return (maxLoc.X + template.Width / 2.0, maxLoc.Y + template.Height / 2.0);

                if (maxVal > bestScore)
                {
                    bestScore = maxVal;
                    bestX = maxLoc.X;
                    bestY = maxLoc.Y;
                    bestW = template.Width;
                    bestH = template.Height;
                }
            }

            return bestScore >= threshold ? (bestX + bestW / 2.0, bestY + bestH / 2.0) : null;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "ImageMatcher error for {Asset}", assetRelPath);
            return null;
        }
    }

    private string ResolveAsset(string path)
    {
        string resolved = Path.IsPathRooted(path)
            ? path
            : Path.Combine(_assetsDir, path.Replace('/', Path.DirectorySeparatorChar));

        if (string.IsNullOrEmpty(Path.GetExtension(resolved)))
            resolved += ".png";

        return resolved;
    }
}
