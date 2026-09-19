using System;
using System.Collections.Generic;
using System.Reflection;
using System.Runtime.Serialization;
using System.Text;
using cohtml.Net;

namespace TurkishLocalization
{
    /// <summary>
    /// Sits in front of the game's cohtml text transformation manager (the embedder callback behind
    /// CSS text-transform) and applies the Turkish i rules before the game's invariant mapping runs.
    /// </summary>
    internal sealed class TurkishCaseMapper : ITextTransformationManager
    {
        private ITextTransformationManager m_Inner;

        // Never called: instances are created without running any constructor, see Install().
        private TurkishCaseMapper() { }

        public override bool CaseMapCharacters(CaseOperation operation, string utf8Text, uint bytesCount, TransformationResult transformed)
        {
            if (TurkishCasing.Enabled && !string.IsNullOrEmpty(utf8Text))
            {
                try
                {
                    string mapped = TurkishCasing.PreMap((int)operation, utf8Text);
                    if (!ReferenceEquals(mapped, utf8Text))
                    {
                        utf8Text = mapped;
                        bytesCount = (uint)Encoding.UTF8.GetByteCount(mapped);
                    }
                }
                catch (Exception)
                {
                    // fall through with the untouched text
                }
            }
            return m_Inner.CaseMapCharacters(operation, utf8Text, bytesCount, transformed);
        }

        // ------------------------------------------------------------------ hook

        private static Dictionary<IntPtr, ITextTransformationManager> s_Instances;
        private static readonly List<KeyValuePair<IntPtr, ITextTransformationManager>> s_Originals =
            new List<KeyValuePair<IntPtr, ITextTransformationManager>>();

        /// <summary>
        /// cohtml calls back into managed code through a static SWIG director thunk that looks the target up in
        /// ITextTransformationManager.Instances by native pointer. The native system cannot be given a new manager
        /// after it was created, but the dictionary entry can point at a wrapper. Returns the number of managers wrapped,
        /// or -1 when the dictionary was not found.
        /// </summary>
        public static int Install()
        {
            if (s_Instances == null)
            {
                FieldInfo field = typeof(ITextTransformationManager).GetField("Instances", BindingFlags.Static | BindingFlags.NonPublic);
                s_Instances = field?.GetValue(null) as Dictionary<IntPtr, ITextTransformationManager>;
                if (s_Instances == null)
                {
                    return -1;
                }
            }

            int count = 0;
            foreach (KeyValuePair<IntPtr, ITextTransformationManager> pair in new List<KeyValuePair<IntPtr, ITextTransformationManager>>(s_Instances))
            {
                if (pair.Value == null || pair.Value is TurkishCaseMapper)
                {
                    continue;
                }
                // No constructor: the base constructor would allocate a second native manager and add a key to the
                // dictionary. The wrapper owns no native object (its handle stays zero, so Dispose/finalizer are no-ops).
                var wrapper = (TurkishCaseMapper)FormatterServices.GetUninitializedObject(typeof(TurkishCaseMapper));
                wrapper.m_Inner = pair.Value;
                s_Instances[pair.Key] = wrapper; // existing key: no rehash, the native side is untouched
                s_Originals.Add(pair);
                count++;
            }
            return count;
        }

        public static void Uninstall()
        {
            if (s_Instances != null)
            {
                foreach (KeyValuePair<IntPtr, ITextTransformationManager> pair in s_Originals)
                {
                    if (s_Instances.TryGetValue(pair.Key, out ITextTransformationManager current) && current is TurkishCaseMapper)
                    {
                        s_Instances[pair.Key] = pair.Value;
                    }
                }
            }
            s_Originals.Clear();
        }
    }
}
