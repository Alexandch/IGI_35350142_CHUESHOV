# text_analyzer.py
import re
import zipfile

class TextAnalyzer:
    """Class to analyze text using regular expressions."""
    def __init__(self, input_file):
        """Initialize with input file and read text."""
        with open(input_file, 'r', encoding='utf-8') as f:
            self.text = f.read()
        self.sentences = re.split(r'(?<=[.!?])\s+', self.text.strip())

    def count_sentences(self):
        """Count total sentences and classify by type."""
        total = len(self.sentences)
        narrative = sum(1 for s in self.sentences if s.endswith('.'))
        interrogative = sum(1 for s in self.sentences if s.endswith('?'))
        imperative = sum(1 for s in self.sentences if s.endswith('!'))
        return total, narrative, interrogative, imperative

    def avg_sentence_length(self):
        """Average sentence length in characters (words only)."""
        word_lengths = [sum(len(w) for w in re.findall(r"[a-zA-Z']+", s.lower())) 
                        for s in self.sentences]
        return sum(word_lengths) / len(word_lengths) if word_lengths else 0

    def avg_word_length(self):
        """Average word length in the text."""
        words = re.findall(r"[a-zA-Z']+", self.text.lower())
        return sum(len(w) for w in words) / len(words) if words else 0

    def count_smileys(self):
        """Count smileys matching the pattern."""
        return len(re.findall(r'[:;]-*(?:\(+|\)+|\[+|\]+)', self.text))

    def apostrophe_sentences(self):
        """Find sentences with apostrophes."""
        return [s for s in self.sentences if "'" in s]

    def replace_time(self):
        """Replace time strings with (TBD)."""
        pattern = r'\b([01]\d|2[0-3]):([0-5]\d)(:([0-5]\d))?\b'
        return re.sub(pattern, '(TBD)', self.text)

    def vowel_ending_words(self):
        """Count words ending with a vowel."""
        return len(re.findall(r"\b[a-zA-Z']*[aeiouy]\b", self.text.lower()))

    def words_by_avg_length(self):
        """Find words matching the average length."""
        words = re.findall(r"[a-zA-Z']+", self.text.lower())
        avg_len = round(self.avg_word_length())
        matching_words = [w for w in words if len(w) == avg_len]
        return avg_len, matching_words if matching_words else f"No words of length {avg_len}"

    def every_fifth_word(self):
        """Extract every fifth word."""
        words = re.findall(r"[a-zA-Z']+", self.text.lower())
        return words[4::5]

    def save_and_archive(self, output_file, archive_file):
        """Save results to file and archive it."""
        with open(output_file, 'w', encoding='utf-8') as f:
            total, narr, inter, imper = self.count_sentences()
            f.write(f"Total sentences: {total}\n")
            f.write(f"Narrative: {narr}, Interrogative: {inter}, Imperative: {imper}\n")
            f.write(f"Avg sentence length: {self.avg_sentence_length():.2f}\n")
            f.write(f"Avg word length: {self.avg_word_length():.2f}\n")
            f.write(f"Smileys: {self.count_smileys()}\n")
            f.write("Sentences with apostrophes:\n" + "\n".join(self.apostrophe_sentences()) + "\n")
            f.write(f"Text with time replaced:\n{self.replace_time()}\n")
            f.write(f"Words ending with vowel: {self.vowel_ending_words()}\n")
            avg_len, words = self.words_by_avg_length()
            f.write(f"Avg word length: {avg_len}\nWords: {words}\n")
            f.write(f"Every fifth word: {self.every_fifth_word()}\n")
        
        with zipfile.ZipFile(archive_file, 'w') as zf:
            zf.write(output_file)
        
        with zipfile.ZipFile(archive_file, 'r') as zf:
            info = zf.getinfo(output_file)
            print(f"Archived file size: {info.file_size} bytes")

# main.py
def main():
    analyzer = TextAnalyzer("input.txt")
    analyzer.save_and_archive("output.txt", "output.zip")

if __name__ == "__main__":
    main()