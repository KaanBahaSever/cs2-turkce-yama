using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Text;
using System.Threading;
using Colossal.Localization;
using Colossal.Logging;
using Game;
using Game.Modding;
using Game.SceneFlow;
using Newtonsoft.Json;
using UnityEngine;

namespace TurkishLocalization
{
    /// <summary>
    /// Standalone Turkish localization for Cities: Skylines II.
    /// Registers a real "tr-TR" locale, so "Türkçe" shows up in Options &gt; Interface &gt; Language
    /// like any built-in language. The translation is embedded in this assembly; no other mod is needed.
    /// </summary>
    public sealed class Mod : IMod
    {
        public const string kLocaleId = "tr-TR";
        public const string kLocalizedName = "Türkçe";

        private const string kResourceName = "TurkishLocalization.Localization.tr-TR.json";
        private const string kOsLocale = "os";

        public static readonly ILog log = LogManager.GetLogger(nameof(TurkishLocalization)).SetShowsErrorsInUI(false);

        private LocalizationManager m_Manager;
        private Dictionary<string, string> m_Entries;
        private MemorySource m_Source;
        private bool m_LocaleAddedByUs;
        private bool m_Busy;

        private CultureInfo m_TurkishCulture;
        private CultureInfo m_PreviousCulture;
        private CultureInfo m_PreviousUICulture;
        private CultureInfo m_PreviousDefaultCulture;
        private CultureInfo m_PreviousDefaultUICulture;
        private bool m_CultureApplied;

        public void OnLoad(UpdateSystem updateSystem)
        {
            try
            {
                m_Manager = GameManager.instance?.localizationManager;
                if (m_Manager == null)
                {
                    log.Error("Localization manager is not available; Turkish localization was not loaded.");
                    return;
                }

                m_Entries = ReadEmbeddedTranslation();
                // Shown by the language selector and by anything that looks a language name up by key.
                m_Entries["Menu.LANGUAGE[" + kLocaleId + "]"] = kLocalizedName;
                m_Entries["Common.LANGUAGE[" + kLocaleId + "]"] = kLocalizedName;
                log.InfoFormat("Read {0} Turkish entries from the embedded resource.", m_Entries.Count);

                m_TurkishCulture = CreateTurkishCulture();

                Register();

                m_Manager.onSupportedLocalesChanged += OnSupportedLocalesChanged;
                m_Manager.onActiveDictionaryChanged += OnActiveDictionaryChanged;

                ActivateOnFirstRun();
                ReapplySavedLocale();
                UpdateCulture();
                WarnAboutLegacyInstall();
            }
            catch (Exception ex)
            {
                log.Error(ex, "Turkish localization failed to load.");
            }
        }

        public void OnDispose()
        {
            try
            {
                if (m_Manager != null)
                {
                    m_Manager.onSupportedLocalesChanged -= OnSupportedLocalesChanged;
                    m_Manager.onActiveDictionaryChanged -= OnActiveDictionaryChanged;
                    if (m_Source != null)
                    {
                        m_Manager.RemoveSource(kLocaleId, m_Source);
                    }
                    if (m_LocaleAddedByUs && m_Manager.SupportsLocale(kLocaleId))
                    {
                        m_Manager.RemoveLocale(kLocaleId);
                    }
                }
            }
            catch (Exception ex)
            {
                log.Warn(ex, "Error while unloading Turkish localization.");
            }
            finally
            {
                RestoreCulture();
                m_Source = null;
                m_Manager = null;
            }
        }

        // ------------------------------------------------------------------ data

        private static Dictionary<string, string> ReadEmbeddedTranslation()
        {
            Assembly assembly = typeof(Mod).Assembly;
            using (Stream stream = assembly.GetManifestResourceStream(kResourceName))
            {
                if (stream == null)
                {
                    throw new FileNotFoundException(
                        "Embedded resource '" + kResourceName + "' is missing. Available: " +
                        string.Join(", ", assembly.GetManifestResourceNames()));
                }
                using (var reader = new StreamReader(stream, Encoding.UTF8))
                {
                    Dictionary<string, string> raw = JsonConvert.DeserializeObject<Dictionary<string, string>>(reader.ReadToEnd());
                    // Copy with the indexer: a null value or a repeated key can never throw here.
                    var entries = new Dictionary<string, string>(raw?.Count ?? 0, StringComparer.Ordinal);
                    if (raw != null)
                    {
                        foreach (KeyValuePair<string, string> pair in raw)
                        {
                            if (!string.IsNullOrWhiteSpace(pair.Key) && pair.Value != null)
                            {
                                entries[pair.Key] = pair.Value;
                            }
                        }
                    }
                    return entries;
                }
            }
        }

        // ---------------------------------------------------------- registration

        /// <summary>
        /// Makes sure the "tr-TR" locale exists and our source is attached to it.
        /// Safe to call repeatedly; never throws on a locale or key that is already there.
        /// </summary>
        private void Register()
        {
            bool existed = m_Manager.SupportsLocale(kLocaleId);
            if (existed)
            {
                log.InfoFormat("Locale '{0}' is already registered (I18N Everywhere or another mod). " +
                               "Merging: entries of this mod take precedence.", kLocaleId);
            }
            else
            {
                AddLocale();
            }

            int overlapping = existed ? CountOverlappingKeys() : 0;

            // The manager remembers every source it has ever been given and ignores one it already knows,
            // so a re-registration always needs a fresh instance.
            if (m_Source != null)
            {
                m_Manager.RemoveSource(kLocaleId, m_Source);
            }
            m_Source = new MemorySource(m_Entries);
            m_Manager.AddSource(kLocaleId, m_Source);

            if (overlapping > 0)
            {
                log.InfoFormat("{0} '{1}' keys were already defined by another source and have been overridden.",
                    overlapping, kLocaleId);
            }

            // AddSource does not refresh a dictionary that is already on screen.
            if (m_Manager.activeLocaleId == kLocaleId)
            {
                m_Manager.ReloadActiveLocale();
            }
            log.InfoFormat("Turkish localization registered: {0} entries under '{1}'.", m_Entries.Count, kLocaleId);
        }

        private void AddLocale()
        {
            // AddLocale throws if the SystemLanguage is already mapped to another locale id, so pick a free one.
            SystemLanguage language = SystemLanguage.Turkish;
            foreach (string id in m_Manager.GetSupportedLocales())
            {
                if (id != kLocaleId && m_Manager.LocaleIdToSystemLanguage(id) == SystemLanguage.Turkish)
                {
                    log.InfoFormat("SystemLanguage.Turkish is already mapped to '{0}'; registering '{1}' without an OS mapping.", id, kLocaleId);
                    language = FindFreeSystemLanguage();
                    break;
                }
            }

            try
            {
                m_Manager.AddLocale(kLocaleId, language, kLocalizedName);
                m_LocaleAddedByUs = true;
            }
            catch (ArgumentException ex)
            {
                // A stale name/language entry from an earlier registration. The locale itself is in place by now.
                log.Info("Locale bookkeeping already contained '" + kLocaleId + "': " + ex.Message);
                m_LocaleAddedByUs = m_Manager.SupportsLocale(kLocaleId);
            }
        }

        private SystemLanguage FindFreeSystemLanguage()
        {
            var used = new HashSet<SystemLanguage>();
            foreach (string id in m_Manager.GetSupportedLocales())
            {
                used.Add(m_Manager.LocaleIdToSystemLanguage(id));
            }
            foreach (SystemLanguage candidate in (SystemLanguage[])Enum.GetValues(typeof(SystemLanguage)))
            {
                if (candidate != SystemLanguage.Unknown && !used.Contains(candidate))
                {
                    return candidate;
                }
            }
            return SystemLanguage.Unknown;
        }

        private int CountOverlappingKeys()
        {
            if (m_Manager.activeLocaleId != kLocaleId || m_Manager.activeDictionary == null)
            {
                return 0;
            }
            int count = 0;
            foreach (string key in m_Entries.Keys)
            {
                if (m_Manager.activeDictionary.ContainsID(key, true))
                {
                    count++;
                }
            }
            return count;
        }

        /// <summary>The game drops every locale on a bulk asset reload; put ours back.</summary>
        private void OnSupportedLocalesChanged()
        {
            if (m_Busy || m_Manager == null || m_Manager.SupportsLocale(kLocaleId))
            {
                return;
            }
            m_Busy = true;
            try
            {
                log.Info("Locale list was rebuilt by the game; registering Turkish again.");
                m_LocaleAddedByUs = false;
                Register();
                ReapplySavedLocale();
            }
            catch (Exception ex)
            {
                log.Warn(ex, "Could not re-register Turkish localization.");
            }
            finally
            {
                m_Busy = false;
            }
        }

        private void OnActiveDictionaryChanged()
        {
            UpdateCulture();
        }

        // -------------------------------------------------------------- settings

        /// <summary>
        /// The saved language is applied before mods load, when "tr-TR" does not exist yet and is silently ignored.
        /// Apply it again now that the locale is there. "os" resolves to Turkish on a Turkish system.
        /// </summary>
        private void ReapplySavedLocale()
        {
            string saved = GameManager.instance?.settings?.userInterface?.locale;
            if (saved == kLocaleId || saved == kOsLocale)
            {
                m_Manager.SetActiveLocale(saved);
            }
        }

        /// <summary>Switch to Turkish once, the first time the mod runs. Afterwards the player's choice is respected.</summary>
        private void ActivateOnFirstRun()
        {
            try
            {
                string folder = Path.Combine(Application.persistentDataPath, "ModsData", nameof(TurkishLocalization));
                string marker = Path.Combine(folder, "activated");
                if (File.Exists(marker))
                {
                    return;
                }
                Directory.CreateDirectory(folder);
                File.WriteAllText(marker, "Turkish was selected automatically on first run. Delete this file to repeat that once.");

                var ui = GameManager.instance?.settings?.userInterface;
                if (ui != null && ui.locale != kLocaleId)
                {
                    ui.locale = kLocaleId;
                    ui.ApplyAndSave();
                    log.Info("First run: game language set to Türkçe. It can be changed in Options > Interface.");
                }
            }
            catch (Exception ex)
            {
                log.Warn(ex, "First-run language activation was skipped.");
            }
        }

        // --------------------------------------------------------------- culture

        /// <summary>
        /// Turkish casing rules (i/İ, ı/I) with invariant number formatting: keeps "1.5" parsing as 1.5
        /// for every piece of code that forgets to pass a culture.
        /// </summary>
        private static CultureInfo CreateTurkishCulture()
        {
            try
            {
                var culture = (CultureInfo)CultureInfo.GetCultureInfo(kLocaleId).Clone();
                culture.NumberFormat = (NumberFormatInfo)CultureInfo.InvariantCulture.NumberFormat.Clone();
                return culture;
            }
            catch (Exception ex)
            {
                log.Info("Culture '" + kLocaleId + "' is not available on this runtime: " + ex.Message);
                return null;
            }
        }

        /// <summary>Turkish culture while Turkish is the active language, the original culture otherwise.</summary>
        private void UpdateCulture()
        {
            if (m_Manager != null && m_Manager.activeLocaleId == kLocaleId)
            {
                ApplyCulture();
            }
            else
            {
                RestoreCulture();
            }
        }

        private void ApplyCulture()
        {
            if (m_CultureApplied || m_TurkishCulture == null)
            {
                return;
            }
            m_PreviousCulture = Thread.CurrentThread.CurrentCulture;
            m_PreviousUICulture = Thread.CurrentThread.CurrentUICulture;
            m_PreviousDefaultCulture = CultureInfo.DefaultThreadCurrentCulture;
            m_PreviousDefaultUICulture = CultureInfo.DefaultThreadCurrentUICulture;

            CultureInfo.DefaultThreadCurrentCulture = m_TurkishCulture;
            CultureInfo.DefaultThreadCurrentUICulture = m_TurkishCulture;
            Thread.CurrentThread.CurrentCulture = m_TurkishCulture;
            Thread.CurrentThread.CurrentUICulture = m_TurkishCulture;
            m_CultureApplied = true;
            log.Info("Thread culture set to tr-TR.");
        }

        private void RestoreCulture()
        {
            if (!m_CultureApplied)
            {
                return;
            }
            CultureInfo.DefaultThreadCurrentCulture = m_PreviousDefaultCulture;
            CultureInfo.DefaultThreadCurrentUICulture = m_PreviousDefaultUICulture;
            if (m_PreviousCulture != null)
            {
                Thread.CurrentThread.CurrentCulture = m_PreviousCulture;
            }
            if (m_PreviousUICulture != null)
            {
                Thread.CurrentThread.CurrentUICulture = m_PreviousUICulture;
            }
            m_CultureApplied = false;
            log.Info("Thread culture restored.");
        }

        // ---------------------------------------------------------------- legacy

        /// <summary>Earlier releases shipped as an I18N Everywhere data file that turned *English* into Turkish.</summary>
        private static void WarnAboutLegacyInstall()
        {
            try
            {
                string legacy = Path.Combine(Application.persistentDataPath, "Mods", "TurkishLang", "lang", "en-US.json");
                if (File.Exists(legacy))
                {
                    log.Warn("An old I18N Everywhere based install was found and is no longer needed. Please delete: " +
                             Path.GetDirectoryName(Path.GetDirectoryName(legacy)));
                }
            }
            catch (Exception)
            {
                // informational only
            }
        }
    }
}
