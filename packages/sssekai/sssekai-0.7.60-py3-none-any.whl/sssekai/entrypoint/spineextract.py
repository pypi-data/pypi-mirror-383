import os
from sssekai.unity.AssetBundle import load_assetbundle
from UnityPy.enums import ClassIDType
from logging import getLogger

logger = getLogger(__name__)


def main_spineextract(args):
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    with open(args.infile, "rb") as f:
        env = load_assetbundle(f)
        objects = [(pobj, pobj.read()) for pobj in env.objects]
        binaries = {
            obj.m_Name: obj
            for pobj, obj in objects
            if pobj.type in {ClassIDType.TextAsset}
        }
        textures = {
            obj.m_Name: obj
            for pobj, obj in objects
            if pobj.type in {ClassIDType.Texture2D}
        }
        spines = set()
        for name in binaries:
            if name.endswith(".atlas") or name.endswith(".skel"):
                spines.add(".".join(name.split(".")[:-1]))
        for spine in spines:
            logger.info("Extracting %s" % spine)
            atlas = binaries.get(spine + ".atlas", None)
            skel = binaries.get(spine + ".skel", None)
            os.makedirs(os.path.join(outdir, spine), exist_ok=True)
            if atlas:
                logger.info("...has Atlas %s" % spine)
                with open(os.path.join(outdir, spine, spine + ".atlas.txt"), "wb") as f:
                    f.write(atlas.m_Script.encode("utf-8", "surrogateescape"))
                texfiles = [line.strip() for line in atlas.m_Script.split("\n")]
                texfiles = [
                    ".".join(line.split(".")[:-1])
                    for line in texfiles
                    if (line.endswith(".png"))
                ]
                for tex in texfiles:
                    logger.info("...has Texture %s" % tex)
                    textureobj = textures.get(tex, None)
                    if textureobj:
                        textureobj.image.save(os.path.join(outdir, spine, tex + ".png"))
                    else:
                        logger.warning("No texture found for %s" % tex)
            else:
                logger.warning(
                    "No atlas found for %s. Consequnetially, no textures cannot be exported either."
                    % spine
                )

            if skel:
                logger.info("...has Skeleton %s" % spine)
                with open(
                    os.path.join(outdir, spine, spine + ".skel.bytes"), "wb"
                ) as f:
                    f.write(skel.m_Script.encode("utf-8", "surrogateescape"))
            else:
                logger.warning("No skel found for %s" % spine)
