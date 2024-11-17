from fastapi import FastAPI, File
from fastapi.responses import Response
from typing import Annotated
from tempfile import NamedTemporaryFile, TemporaryDirectory
from subprocess import check_output
from io import BytesIO
from pathlib import Path
from logging import getLogger

app = FastAPI()

log = getLogger("uvicorn.error")


@app.post("/")
async def create_item(pdb: Annotated[bytes, File()], ligand: str):
    with TemporaryDirectory() as tmpdir:
        with (
            NamedTemporaryFile(dir=tmpdir, suffix=".pdb") as fp,
            NamedTemporaryFile(dir=tmpdir, suffix=".txt") as tmp,
        ):
            fp.write(pdb)
            tmp.write(f"{fp.name}\t{ligand}".encode())
            tmp.flush()

            log.info(
                "Input file content: '%s'",
                Path(tmp.name).read_text(),
            )

            result = check_output(
                ["dpocket", "-f", tmp.name, "-v", "10000", "-d", "5.0"],
                cwd=tmpdir,
            )

            log.info(
                "Output:\n\t\t%s",
                result.decode().replace("\n", "\n\t\t"),
            )
            log.info(
                "Files in tempdir: \n\t\t%s",
                "\n\t\t".join(map(str, Path(tmpdir).rglob("*"))),
            )
            data = BytesIO((Path(tmpdir) / "dpout_explicitp.txt").read_bytes())
            return Response(content=data.getvalue(), media_type="text/plain")
