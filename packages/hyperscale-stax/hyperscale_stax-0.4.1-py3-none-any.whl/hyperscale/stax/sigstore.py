from sigstore.models import Bundle
from sigstore.verify.policy import Identity
from sigstore.verify.verifier import Verifier

verifier = Verifier.production()


def verify_bundle_signature(archive_path, sigstore_bundle, oidc_identity, oidc_issuer):
    with open(archive_path, "rb") as f1:
        data = f1.read()

        with open(sigstore_bundle) as f2:
            json = f2.read()
            bundle = Bundle.from_json(json)

            policy = Identity(
                identity=oidc_identity,
                issuer=oidc_issuer,
            )

            verifier.verify_artifact(data, bundle, policy)
