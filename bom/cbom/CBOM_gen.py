import json
import os
import uuid
from datetime import datetime

FILENAME = "cbom.json"


# 生成uuid
def generate_uuid():
    return f"urn:uuid:{str(uuid.uuid4())}"


# 生成时间戳
def generate_timestamp():
    return datetime.utcnow().isoformat() + "Z"


# 加载cbom，初始化cbom
def load_bom(filename=FILENAME):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    else:
        return {
            "bomFormat": "CycloneDX",
            "specVersion": "1.6",
            "serialNumber": generate_uuid(),
            "version": 1,
            "metadata": {
                "timestamp": generate_timestamp(),
                "component": {
                    "type": "application",
                    "name": "default-crypto-app"
                }
            },
            "components": [],
            "dependencies": []
        }


# 保存cbom
def save_bom(bom_data, filename=FILENAME):
    with open(filename, "w") as f:
        json.dump(bom_data, f, indent=2)


# bom_ref 重复检查 + 添加组件
def component_exists(bom_data, bom_ref):
    return any(comp.get("bom-ref") == bom_ref for comp in bom_data["components"])


def add_component(bom_data, component):
    bom_ref = component.get("bom-ref")
    if not bom_ref:
        raise ValueError("Component must have a 'bom-ref' field.")

    if component_exists(bom_data, bom_ref):
        print(f"[SKIP] Component '{bom_ref}' already exists.")
    else:
        bom_data["components"].append(component)
        print(f"[ADD] Component '{bom_ref}' added.")


# 添加依赖
def add_dependency(bom_data, ref, depends_on=None, provides=None):
    dep = {"ref": ref}
    if depends_on:
        dep["dependsOn"] = depends_on
    if provides:
        dep["provides"] = provides
    bom_data["dependencies"].append(dep)


# ---------- Asset Builders ----------
# 构建算法
def build_algorithm(name, primitive, parameter_set, mode, platform, functions, oid, classical_level, nist_level) -> dict:
    return {
        "type": "cryptographic-asset",
        "bom-ref": f"crypto/algorithm/{name.lower().replace(' ', '-')}@{oid}",
        "name": name,
        "cryptoProperties": {
            "assetType": "algorithm",
            "algorithmProperties": {
                "primitive": primitive,
                "parameterSetIdentifier": parameter_set,
                "mode": mode,
                "executionEnvironment": "software-plain-ram",
                "implementationPlatform": platform,
                "certificationLevel": ["none"],
                "cryptoFunctions": functions,
                "classicalSecurityLevel": classical_level,
                "nistQuantumSecurityLevel": nist_level
            },
            "oid": oid
        }
    }


# 构建key
def build_key(name, key_type, size, oid, algorithm_ref, state="active", secured_by=None, creation=None,
              activation=None) -> dict:
    return {
        "type": "cryptographic-asset",
        "bom-ref": f"crypto/key/{name.lower().replace(' ', '-')}@{oid}",
        "name": name,
        "cryptoProperties": {
            "assetType": "related-crypto-material",
            "relatedCryptoMaterialProperties": {
                "type": key_type,
                "id": str(uuid.uuid4()),
                "state": state,
                "size": size,
                "algorithmRef": algorithm_ref,
                "securedBy": secured_by or {"mechanism": "None"},
                "creationDate": creation or generate_timestamp(),
                "activationDate": activation or generate_timestamp()
            },
            "oid": oid
        }
    }


# 构建证书
def build_certificate(name, subject_name, issuer_name, valid_from, valid_to, sig_algo_ref, pubkey_ref,
                      certificateFormat, certificateExtension) -> dict:
    return {
        "type": "cryptographic-asset",
        "bom-ref": f"crypto/certificate/{name.lower()}@sha256:{uuid.uuid4().hex}",
        "name": name,
        "cryptoProperties": {
            "assetType": "certificate",
            "certificateProperties": {
                "subjectName": subject_name,
                "issuerName": issuer_name,
                "notValidBefore": valid_from,
                "notValidAfter": valid_to,
                "signatureAlgorithmRef": sig_algo_ref,
                "subjectPublicKeyRef": pubkey_ref,
                "certificateFormat": certificateFormat,
                "certificateExtension": certificateExtension
            }
        }
    }


# 构建协议
def build_protocol(name, proto_type, version, cipher_suites, crypto_refs, oid) -> dict:
    return {
        "type": "cryptographic-asset",
        "bom-ref": f"crypto/protocol/{proto_type}@{version}",
        "name": name,
        "cryptoProperties": {
            "assetType": "protocol",
            "protocolProperties": {
                "type": proto_type,
                "version": version,
                "cipherSuites": cipher_suites,
                "cryptoRefArray": crypto_refs
            },
            "oid": oid
        }
    }


# 构建其他密码相关材料
def build_Other(name, CryptoRelatedType, generate_methed, store_location) -> dict:
    return {
        "type": "cryptographic_asset",
        "bom-ref": f"other/{name.lower()}@{CryptoRelatedType}",
        "name": name,
        "version": CryptoRelatedType,
        "generate_methed": generate_methed,
        "store_location": store_location
    }


# 构建依赖库 - cpe
def build_library(name, version) -> dict:
    return {
        "type": "library",
        "bom-ref": f"lib/{name.lower()}@{version}",
        "name": name,
        "version": version
    }


# 构建数据
def build_Data(name, access_mode, VolumeMode, DataType, need_protect, pro_measures, pro_ref) -> dict:
    return {
        "type": "data",
        "name": name,
        "bom-ref": f"data/{name.lower()}@{DataType}",
        "access_mode": access_mode,
        "VolumeMode": VolumeMode,
        "DataType": DataType,
        "need_protect": need_protect,
        "pro_measures": pro_measures,
        "pro_ref": pro_ref
    }


# 构建功能-此处特指安全功能
def build_App(name, TriggerType, input_type, output_type, step, execution_environment, resourceReferences) -> dict:
    return {
        "type": "application",
        "bom-ref": f"app/{name.lower()}",
        "name": name,
        "TriggerType": TriggerType,
        "input_type": input_type,
        "output_type": output_type,
        "step": step,
        "execution_environment": execution_environment,
        "resourceReferences": resourceReferences
    }


if __name__ == "__main__":
    bom = load_bom()
    # -------------------------------------------------------------------------
    # 示例
    # 1. 协议组件 TLSv1.2
    tls_protocol = build_protocol(
        name="TLSv1.2",
        proto_type="tls",
        version="1.2",
        cipher_suites=[
            {
                "name": "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
                "algorithms": [
                    "crypto/algorithm/ecdh-curve25519@1.3.132.1.12",
                    "crypto/algorithm/rsa-2048@1.2.840.113549.1.1.1",
                    "crypto/algorithm/aes-256-gcm@2.16.840.1.101.3.4.1.46",
                    "crypto/algorithm/sha-384@2.16.840.1.101.3.4.2.9"
                ],
                "identifiers": ["0xC0", "0x30"]
            }
        ],
        crypto_refs=[
            "crypto/certificate/google.com@sha256:1e15e0fbd3ce95bde5945633ae96add551341b11e5bae7bba12e98ad84a5beb4"
        ],
        oid="1.3.18.0.2.32.104"
    )
    add_component(bom, tls_protocol)

    # 2. 算法组件们
    add_component(bom, build_algorithm("ECDH", None, None, None, "x86_64", ["keygen"], "1.3.132.1.12", None, None))
    add_component(bom, build_algorithm("RSA-2048", None, "2048", None, "x86_64", ["encapsulate", "decapsulate"],
                                       "1.2.840.113549.1.1.1", None, None))
    add_component(bom, build_algorithm("AES-256-GCM", "ae", "256", "gcm", "x86_64", ["encrypt", "decrypt"],
                                       "2.16.840.1.101.3.4.1.46", 256, 1))
    add_component(bom,
                  build_algorithm("SHA384", None, "384", None, "x86_64", ["digest"], "2.16.840.1.101.3.4.2.9", None,
                                  2))
    add_component(bom,
                  build_algorithm("SHA512withRSA", None, "512", None, "x86_64", ["digest"], "1.2.840.113549.1.1.13",
                                  None, 0))

    # 3. key组件
    rsa_key = build_key(
        name="RSA-2048",
        key_type="public-key",
        size=2048,
        oid="1.2.840.113549.1.1.1",
        algorithm_ref="crypto/algorithm/rsa-2048@1.2.840.113549.1.1.1",
        secured_by={
            "mechanism": "Software",
            "algorithmRef": "crypto/algorithm/aes-256-gcm@2.16.840.1.101.3.4.1.46"
        },
        creation="2016-11-21T08:00:00Z",
        activation="2016-11-21T08:20:00Z"
    )
    add_component(bom, rsa_key)

    # 4. 证书组件
    cert = build_certificate(
        name="google.com",
        subject_name="CN = www.google.com",
        issuer_name="C = US, O = Google Trust Services LLC, CN = GTS CA 1C3",
        valid_from="2016-11-21T08:00:00Z",
        valid_to="2017-11-22T07:59:59Z",
        sig_algo_ref="crypto/algorithm/sha-512-rsa@1.2.840.113549.1.1.13",
        pubkey_ref="crypto/key/rsa-2048@1.2.840.113549.1.1.1",
        certificateFormat="X.509",
        certificateExtension="crt"
    )
    add_component(bom, cert)

    # 保存
    save_bom(bom)
