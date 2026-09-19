using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using System.Text;

namespace TurkishLocalization
{
    /// <summary>
    /// Turkish-aware preparation of text for CSS text-transform.
    ///
    /// Gameface does not case-map text itself; it asks the game, and the game answers with
    /// <c>ToUpperInvariant()</c>. Invariant casing turns "i" into "I" and leaves the dotless "ı" (U+0131)
    /// alone, which is why upper-cased Turkish shows up as "PARADOX HESABı" and "GRAFIK".
    /// The four Turkish i letters are mapped here first; everything else is left to the game's own mapper.
    /// </summary>
    internal static class TurkishCasing
    {
        // Same numeric values as cohtml.Net.ITextTransformationManager.CaseOperation.
        public const int kUppercase = 0;
        public const int kLowercase = 1;
        public const int kCapitalize = 2;

        private const char kDotlessSmall = 'ı';  // ı
        private const char kDottedCapital = 'İ'; // İ
        private const string kResourceName = "TurkishLocalization.Localization.protected-words.txt";

        /// <summary>Set from the main thread when the active locale changes; read from the UI callback.</summary>
        public static volatile bool Enabled;

        /// <summary>Foreign names that keep international casing (CITIES: SKYLINES, not CİTİES: SKYLİNES). Replaced as a whole, never mutated.</summary>
        private static volatile HashSet<string> s_Protected = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "Cities", "Skylines", "Chirper", "Paradox", "Interactive",
        };

        public static int ProtectedCount => s_Protected.Count;

        /// <summary>Loads the generated word list (tools/build_protected_words.py) from the assembly.</summary>
        public static void LoadProtectedWords(Assembly assembly)
        {
            using (Stream stream = assembly.GetManifestResourceStream(kResourceName))
            {
                if (stream == null)
                {
                    return;
                }
                var words = new HashSet<string>(s_Protected, StringComparer.OrdinalIgnoreCase);
                using (var reader = new StreamReader(stream, Encoding.UTF8))
                {
                    string line;
                    while ((line = reader.ReadLine()) != null)
                    {
                        line = line.Trim();
                        if (line.Length > 0 && line[0] != '#')
                        {
                            words.Add(line);
                        }
                    }
                }
                s_Protected = words;
            }
        }

        /// <summary>Returns the same instance when nothing has to change (no allocation on the hot path).</summary>
        public static string PreMap(int operation, string text)
        {
            if (string.IsNullOrEmpty(text))
            {
                return text;
            }
            bool lower = operation == kLowercase;
            char a = lower ? 'I' : 'i';
            char b = lower ? kDottedCapital : kDotlessSmall;
            if (text.IndexOf(a) < 0 && text.IndexOf(b) < 0)
            {
                return text;
            }

            HashSet<string> protectedWords = s_Protected;
            StringBuilder result = null;
            int i = 0;
            while (i < text.Length)
            {
                if (!char.IsLetter(text[i]))
                {
                    i++;
                    continue;
                }
                int start = i;
                bool hit = false;
                bool foreign = false;
                while (i < text.Length && char.IsLetter(text[i]))
                {
                    char c = text[i];
                    hit |= c == a || c == b;
                    // q, w and x do not exist in Turkish: Windows, Twitch, Xbox, DirectX, "New Oxford"...
                    foreign |= c == 'q' || c == 'w' || c == 'x' || c == 'Q' || c == 'W' || c == 'X';
                    i++;
                }
                if (!hit || foreign || protectedWords.Contains(text.Substring(start, i - start)))
                {
                    continue;
                }
                int end = operation == kCapitalize ? start + 1 : i; // capitalize touches the first letter only
                for (int k = start; k < end; k++)
                {
                    char c = text[k];
                    char mapped = c;
                    if (lower)
                    {
                        if (c == 'I') mapped = kDotlessSmall;
                        else if (c == kDottedCapital) mapped = 'i';
                    }
                    else
                    {
                        if (c == 'i') mapped = kDottedCapital;
                        else if (c == kDotlessSmall) mapped = 'I';
                    }
                    if (mapped != c)
                    {
                        if (result == null) result = new StringBuilder(text);
                        result[k] = mapped;
                    }
                }
            }
            return result == null ? text : result.ToString();
        }
    }
}
