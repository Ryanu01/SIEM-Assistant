#req libraries

pip install upgrade transformers accelerate datasets

import pandas as pd
from datasets import Dataset

file_path = 'colab.json'#our actuall dataset 
data = pd.read_json(file_path)


df = pd.DataFrame(data)
hf_dataset = Dataset.from_pandas(df)  # hugging  face k liye dataset is the only option to store data


dataset = hf_dataset.train_test_split(test_size=0.2) #80 perc for training and remaining 20% for testing

print("--- Initial Dataset ---")
print(dataset)

#Tokenizers

from transformers import AutoTokenizer

model_name = "google/flan-t5-small"    # loading our actual mmodel
tokenizer = AutoTokenizer.from_pretrained(model_name)

prefix = "translate to Wazuh query: "

def preprocess_function(examples):
    """This function tokenizes and pads the input and target texts."""
    inputs = [prefix + doc for doc in examples["instruction"]]
    
    # Tokenize and pad the inputs (instructions)
    model_inputs = tokenizer(inputs, max_length=128, truncation=True, padding="max_length")
    
    # Tokenize and pad the targets (queries)
    labels = tokenizer(text_target=examples["query"], max_length=128, truncation=True, padding="max_length")
    
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

tokenized_dataset = dataset.map(preprocess_function, batched=True) # apply the tokenization to the entire dataset

print("\n--- Tokenized Dataset Sample ---")
print(tokenized_dataset["train"][0])


# fine tunning part from hugging face documentation
from transformers import AutoModelForSeq2SeqLM, Seq2SeqTrainingArguments, Seq2SeqTrainer

model = AutoModelForSeq2SeqLM.from_pretrained(model_name)# loading our pretrained model

# Define the training arguments with key changes
training_args = Seq2SeqTrainingArguments(
    output_dir="./wazuh-t5-finetuned",
    
   
    evaluation_strategy="epoch",      # evaluate at the end of each epoch
    save_strategy="epoch",            # save a checkpoint at the end of each epoch
    learning_rate=5e-4,               # increased learning rate
    load_best_model_at_end=True,      # load the best model when training is done
   

    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    weight_decay=0.01,
    save_total_limit=3 ,             # geimini stuff
    num_train_epochs=30,
    predict_with_generate=True,
    fp16=True,
    report_to="none",
)

# createing the Trainer instance (this part is unchanged)
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["test"],
    tokenizer=tokenizer,
)


print("\n Starting Fine-Tuning")
trainer.train()
print("Fine-Tuning Complete")

# save the best fine-tuned model for later use
trainer.save_model("./my-final-wazuh-model")

from transformers import pipeline  # automating the working of this model using scikit-learn pipelines

pipe = pipeline("text2text-generation", model="./my-final-wazuh-model")  # loading the pipeline with the task that model needs to perform and then with the model to use

# Create a new, unseen instruction
new_instruction = "find me critical alerts from agent 002"

# Get the model's prediction
generated_query = pipe(prefix + new_instruction)                  # GEMINI

print("\n--- Inference Test ---")
print(f"Instruction: {new_instruction}")
print(f"Generated Query: {generated_query[0]['generated_text']}")