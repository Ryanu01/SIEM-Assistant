import torch
from datasets import load_dataset
from transformers import T5ForConditionalGeneration, T5Tokenizer, Trainer, TrainingArguments

#loading dataset from JSON and Preprocess
json_filename = 'siem_data.json'
print(f"Loading dataset from '{json_filename}'")

try:
    raw_dataset = load_dataset('json', data_files=json_filename, split='train')
except FileNotFoundError:
    print(f"Error: '{json_filename}' not found. Please run the create_dataset.py script first.")
    exit()

# Split dataset (80/20)
dataset_splits = raw_dataset.train_test_split(test_size=0.2, seed=42)
train_dataset = dataset_splits['train']
eval_dataset = dataset_splits['test']

print(f"Training set size: {len(train_dataset)}")
print(f"Validation set size: {len(eval_dataset)}")
print("-" * 30)

# Prefix instructions for T5
TASK_PREFIX = "translate English to SQL: "
def add_prefix(example):
    example['instruction'] = TASK_PREFIX + example['instruction']
    return example

train_dataset = train_dataset.map(add_prefix)
eval_dataset = eval_dataset.map(add_prefix)

#2. Load Model & Tokenizer and Tokenize Data
MODEL_NAME = 't5-small'
tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)

MAX_LENGTH = 128

def tokenize_data(batch):
    model_inputs = tokenizer(batch['instruction'], max_length=MAX_LENGTH, padding='max_length', truncation=True)
    labels = tokenizer(text_target=batch['query'], max_length=MAX_LENGTH, padding='max_length', truncation=True)
    model_inputs['labels'] = labels['input_ids']
    return model_inputs

train_dataset = train_dataset.map(tokenize_data, batched=True)
eval_dataset = eval_dataset.map(tokenize_data, batched=True)

train_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])
eval_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])

# 3.training Arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=10,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    eval_strategy="epoch",
    logging_strategy="epoch",
    save_strategy="epoch",
    learning_rate=5e-5,
    weight_decay=0.01,
    logging_dir='./logs',
    push_to_hub=False,
    report_to="none"   
)


# --- 4. Trainer ---
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,             

)

# Train model
trainer.train()

# --- 5. Inference ---
def generate_sql(command):
    input_text = f"{TASK_PREFIX}{command}"
    inputs = tokenizer(input_text, return_tensors="pt", max_length=MAX_LENGTH, truncation=True)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    outputs = model.generate(
        inputs['input_ids'],
        attention_mask=inputs['attention_mask'],
        max_length=150,
        num_beams=5,
        early_stopping=True
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

#Example Usage
print("\n Testing the Fine-Tuned Model")
command1 = "Show hosts with more than 10 critical alerts."
sql1 = generate_sql(command1)
print(f"Command: {command1}\n   Generated SQL: {sql1}\n")

command2 = "Find logins that are not from user 'admin'."
sql2 = generate_sql(command2)
print(f"Command: {command2}\n   Generated SQL: {sql2}\n")

command4 = "find successful logins from user ryan between time 1 pm and 3 pm."
sql4 = generate_sql(command4)
print(f"Command: {command4}\n   Generated SQL: {sql4}\n")

command5 = "find logins fails created by user harshil'."
sql5 = generate_sql(command5)
print(f"Command: {command5}\n   Generated SQL: {sql5}\n")
