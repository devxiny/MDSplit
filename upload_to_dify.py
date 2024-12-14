import requests
import json


def upload(
    url: str,
    api_key: str,
    dataset_id: str,
    document_id: str,
    upload_data: dict,
    is_qa: bool,
):
    url = f"{url}/v1/datasets/{dataset_id}/documents/{document_id}/segments"
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    data = None
    if is_qa:
        data = {
            "segments": [
                {
                    "content": upload_data["instruction"],
                    "answer": upload_data["output"],
                    "keywords": [],
                }
            ]
        }
    else:
        data = {
            "segments": [
                {
                    "content": upload_data["instruction"]
                    + "\n"
                    + upload_data["output"],
                    "answer": "",
                    "keywords": [],
                }
            ]
        }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    print(response.text)


def load_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def upload_from_file(file_path, is_qa):
    for item in load_file(file_path):
        upload(
            url="http://10.1.11.201:50002",
            api_key="dataset-MvAhsXH3F67KQEDcuWBgvkvG",
            dataset_id="a53463fa-7cac-476e-842d-3d8bf6f626fd",
            document_id="abd9ecc9-4d15-4d15-a758-26b36eff62ab",
            upload_data=item,
            is_qa=is_qa,
        )


if __name__ == "__main__":
    is_qa = False
    upload_from_file("序-RESULT.json", is_qa=is_qa)
    upload_from_file("第一章-RESULT.json", is_qa=is_qa)
    upload_from_file("第二章-RESULT.json", is_qa=is_qa)
    upload_from_file("第三章-RESULT.json", is_qa=is_qa)
    upload_from_file("第四章-RESULT.json", is_qa=is_qa)
    upload_from_file("第五章-RESULT.json", is_qa=is_qa)
    upload_from_file("第六章-RESULT.json", is_qa=is_qa)
    upload_from_file("尾-RESULT.json", is_qa=is_qa)
