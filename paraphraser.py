import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class Paraphraser:
    def __init__(self, model_name="humarin/chatgpt_paraphraser_on_T5_base"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)

    def paraphrase_article(self, markdown_text):
        lines = markdown_text.split('\n')
        paraphrased_lines = []
        inside_code_block = False  # Flag to track if we're inside a code block

        for line in lines:
            stripped_line = line.strip()

            # Preserve empty lines or lines with only whitespace
            if not stripped_line:
                paraphrased_lines.append(line)
                continue

            # Skip headings and subheadings
            if stripped_line.startswith(('#', '##', '###')):
                paraphrased_lines.append(line)
                continue

            # Check for the start or end of a code block
            if stripped_line.startswith('```') or stripped_line.endswith('```'):
                inside_code_block = not inside_code_block  # Toggle the flag
                paraphrased_lines.append(line)
                continue

            # If inside a code block, add the line as-is without paraphrasing
            if inside_code_block:
                paraphrased_lines.append(line)
                continue

            # Handle bullet points
            if stripped_line.startswith(('-', '*')):
                bullet_point = stripped_line[0]
                content_after_bullet = stripped_line[1:].lstrip()  # Remove bullet and any leading whitespace
                
                # Split content at colon if present
                if ':' in content_after_bullet:
                    main_point, description = content_after_bullet.split(':', 1)
                    
                    # Paraphrase the description
                    paraphrased_description = self._paraphrase_text(description.strip())[0]  # Taking the first paraphrased result
                    
                    # Combine the main point and paraphrased description
                    paraphrased_content = main_point + ': ' + paraphrased_description
                else:
                    # If no colon is present, paraphrase the entire content
                    paraphrased_content = self._paraphrase_text(content_after_bullet)[0]  # Taking the first paraphrased result
                
                # Combine the bullet point, space, and paraphrased content
                paraphrased_line = bullet_point + ' ' + paraphrased_content
                paraphrased_lines.append(paraphrased_line)
                continue


            # Paraphrase other lines (like regular paragraphs)
            paraphrased_line = self._paraphrase_text(stripped_line)[0]  # Taking the first paraphrased result
            paraphrased_lines.append(paraphrased_line)

        # Combine the paraphrased lines
        paraphrased_article = '\n'.join(paraphrased_lines)
        return paraphrased_article


    def _paraphrase_text(self, text):
        return self.paraphrase(text)  # Using the provided paraphrase function

    def paraphrase(
        self,
        text,
        num_beams=5,
        num_beam_groups=5,
        num_return_sequences=5,
        repetition_penalty=10.0,
        diversity_penalty=3.0,
        no_repeat_ngram_size=2,
        temperature=0.7,
        max_length=128
    ):
        sentences = text.split('.')
        paraphrased_sentences = []

        for sentence in sentences:
            if sentence.strip():  # Ensure the sentence is not empty
                input_ids = self.tokenizer(
                    f'paraphrase: {sentence}',
                    return_tensors="pt", padding="longest",
                    max_length=max_length,
                    truncation=True,
                ).input_ids

                outputs = self.model.generate(
                    input_ids, temperature=temperature, repetition_penalty=repetition_penalty,
                    num_return_sequences=1,  # We only want one paraphrased version for each sentence
                    no_repeat_ngram_size=no_repeat_ngram_size,
                    num_beams=num_beams, num_beam_groups=num_beam_groups,
                    max_length=max_length, diversity_penalty=diversity_penalty
                )

                paraphrased_sentence = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                paraphrased_sentences.append(paraphrased_sentence.strip())

        # Combine the paraphrased sentences
        paraphrased_text = '. '.join(paraphrased_sentences)
        return [paraphrased_text]  # Return as a list to maintain compatibility with the rest of the code


if __name__ == "__main__":
    # Sample markdown text
    sample_markdown = """
    One practical application of this technique is in the enhancement of scanned invoices before performing Optical Character Recognition (OCR). In many businesses, invoices are received in various formats and qualities. Some might be scanned copies of printed documents, while others might be photographs taken with mobile devices. These variations introduce challenges for OCR systems, which rely on clear, high-resolution inputs to accurately extract text.

    By employing a super-resolution model trained with perceptual loss from VGG19-extracted features, we can enhance these invoices. The model focuses on preserving and enhancing textual details, ensuring that characters are sharp, clear, and distinguishable. This preprocessing step significantly improves the accuracy of subsequent OCR, ensuring that crucial information like product names, quantities, prices, and dates are correctly extracted.
    """

    # Create an instance of the Paraphraser class
    paraphraser = Paraphraser()

    # Paraphrase the sample markdown text
    paraphrased_markdown = paraphraser.paraphrase_article(sample_markdown)

    # Print the paraphrased markdown
    print(paraphrased_markdown)
