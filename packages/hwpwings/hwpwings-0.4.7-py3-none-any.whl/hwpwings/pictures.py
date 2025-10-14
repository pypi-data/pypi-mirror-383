from typing import Literal
import os
from urllib import request

class pictures:
    
    def insert_picture(self, path: str, sizeoption: int=0):
        """
        HWP 문서에 그림을 삽입하는 메서드입니다.

        Parameters:
            path (str): 삽입할 그림 파일의 경로입니다.
            sizeoption (int): 그림의 크기 옵션을 지정합니다.
                - 0: 이미지 원래 크기로 삽입합니다.
                - 2: 셀 안에 있을 때 셀을 채웁니다 (그림 비율 무시).
                - 3: 셀에 맞추되 그림 비율을 유지하여 크기를 변경합니다.

        Returns:
            삽입된 그림 객체를 반환합니다.
        """
        return self.hwp.InsertPicture(path, sizeoption=sizeoption)
    
    def insert_background_picture(
            self,
            path: str,
            border_type: Literal["SelectedCell", "SelectedCellDelete"] = "SelectedCell",
            embedded: bool = True,
            filloption: int = 5,
            effect: int = 0,
            watermark: bool = False,
            brightness: int = 0,
            contrast: int = 0,
    ) -> bool:
        """
        **셀**에 배경이미지를 삽입한다.

        CellBorderFill의 SetItem 중 FillAttr 의 SetItem FileName 에
        이미지의 binary data를 지정해 줄 수가 없어서 만든 함수다.
        기타 배경에 대한 다른 조정은 Action과 ParameterSet의 조합으로 가능하다.

        Args:
            path: 삽입할 이미지 파일
            border_type:
                배경 유형을 문자열로 지정(파라미터 이름과는 다르게 삽입/제거 기능이다.)

                    - "SelectedCell": 현재 선택된 표의 셀의 배경을 변경한다.
                    - "SelectedCellDelete": 현재 선택된 표의 셀의 배경을 지운다.

                단, 배경 제거시 반드시 셀이 선택되어 있어야함.
                커서가 위치하는 것만으로는 동작하지 않음.

            embedded: 이미지 파일을 문서 내에 포함할지 여부 (True/False). 생략하면 True
            filloption:
                삽입할 그림의 크기를 지정하는 옵션

                    - 0: 바둑판식으로 - 모두
                    - 1: 바둑판식으로 - 가로/위
                    - 2: 바둑판식으로 - 가로/아로
                    - 3: 바둑판식으로 - 세로/왼쪽
                    - 4: 바둑판식으로 - 세로/오른쪽
                    - 5: 크기에 맞추어(기본값)
                    - 6: 가운데로
                    - 7: 가운데 위로
                    - 8: 가운데 아래로
                    - 9: 왼쪽 가운데로
                    - 10: 왼쪽 위로
                    - 11: 왼쪽 아래로
                    - 12: 오른쪽 가운데로
                    - 13: 오른쪽 위로
                    - 14: 오른쪽 아래로

            effect:
                이미지효과

                    - 0: 원래 그림(기본값)
                    - 1: 그레이 스케일
                    - 2: 흑백으로

            watermark: watermark효과 유무(True/False). 기본값은 False. 이 옵션이 True이면 brightness 와 contrast 옵션이 무시된다.
            brightness: 밝기 지정(-100 ~ 100), 기본 값은 0
            contrast: 선명도 지정(-100 ~ 100), 기본 값은 0

        Returns:
            성공했을 경우 True, 실패했을 경우 False

        Examples:
            >>> from pyhwpx import Hwp
            >>> hwp = Hwp()
            >>> hwp.insert_background_picture(path="C:/Users/User/Desktop/KakaoTalk_20230709_023118549.jpg")
            True
        """
        if path.startswith("http"):
            request.urlretrieve(path, os.path.join(os.getcwd(), "temp.jpg"))
            path = os.path.join(os.getcwd(), "temp.jpg")
        elif path and path.lower()[1] != ":":
            path = os.path.join(os.getcwd(), path)

        try:
            return self.hwp.InsertBackgroundPicture(
                Path=path,
                BorderType=border_type,
                Embedded=embedded,
                filloption=filloption,
                Effect=effect,
                watermark=watermark,
                Brightness=brightness,
                Contrast=contrast,
            )
        finally:
            if "temp.jpg" in os.listdir():
                os.remove(path)
    
    def delete_picture(self, target_index:int=1):
        """
        번호에 맞는 그림을 삭제한다
        """
        # 컨트롤정의 및 그림저장 딕셔너리 생성
        ctrl = self.hwp.HeadCtrl
        picture_dict = {}
        index = 1

        # 그림 객체만 딕셔너리로 저장
        while ctrl:
            if ctrl.UserDesc == '그림':
                picture_dict[index] = ctrl.GetAnchorPos(0)
                index += 1
            ctrl = ctrl.Next

        # 그림 번호가 존재하는지 확인 후 삭제
        selected_pos = picture_dict.get(target_index)
        if selected_pos:
            # Move to the selected position and delete the picture
            self.hwp.SetPosBySet(selected_pos)
            self.hwp.FindCtrl()
            self.hwp.HAction.Run("Delete")
            return True
        else:
            # Target index does not exist
            return False

    def delete_all_pictures(self):
        """
        삽입된 모든 그림을 삭제합니다.
        """
        ctrl = self.hwp.HeadCtrl
        picture_deleted = False

        # Iterate through all controls to find and delete pictures
        while ctrl:
            if ctrl.UserDesc == '그림':
                self.hwp.SetPosBySet(ctrl.GetAnchorPos(0))  # 그림객체로 이동
                self.hwp.FindCtrl()
                self.hwp.HAction.Run("Delete")
                picture_deleted = True
            ctrl = ctrl.Next

        return picture_deleted